"""
Render a customer journey map as an SVG file.

Usage:
    python render_map.py journey.json journey.svg

The map has four parts, drawn in this order:
  1. A y-axis with smiley faces (crying at the bottom, ecstatic at the top),
     so anyone can read the feeling without a legend.
  2. Red shading wherever the journey drops below neutral, so the pain
     points jump out at a glance.
  3. The purple journey line, with short "why" callouts on delights.
  4. A dashed green "with fixes" line, with the fix name above each lifted dip.

The input JSON format is described in references/map_format.md.
The code is deliberately plain (explicit loops, named variables) so the
next person can follow it without decoding clever one-liners.
"""

import json
import sys
from html import escape


# ---------------------------------------------------------------------------
# Layout constants. Kept in one place so the look can be tuned without
# hunting through the drawing code.
# ---------------------------------------------------------------------------

AXIS_X = 90             # x position of the vertical (feeling) axis
FIRST_STEP_GAP = 60     # gap between the axis and the first step
STEP_SPACING = 72       # horizontal distance between steps
RIGHT_PADDING = 90      # room on the right for the last callout
PX_PER_SCORE = 55       # vertical pixels for one point on the -2..+2 scale
MIN_WIDTH = 680         # never draw narrower than this, so small maps still look balanced
CHAR_WIDTH_12PX = 6.4   # rough width of one character at 12px, for sizing label space


SCOPE_LINE_HEIGHT = 18  # vertical gap between the scope lines at the top

# Scope fields shown above the map, in reading order: who, what they want,
# what kicked it off, which path we're drawing, and what "done" looks like.
SCOPE_FIELDS = [
    ("Persona", "persona"),
    ("Job to be done", "jtbd"),
    ("Trigger", "trigger"),
    ("Scenario", "scenario"),
    ("Success looks like", "success"),
]

JOURNEY_COLOR = "#7F77DD"   # purple: today's journey
PAIN_COLOR = "#E24B4A"      # red: below-neutral areas
FIX_COLOR = "#639922"       # green: journey with fixes in place
FACE_COLOR = "#378ADD"      # blue: smiley faces, matching the hand-drawn style
AXIS_COLOR = "#5F5E5A"
TEXT_COLOR = "#2C2C2A"
MUTED_TEXT = "#5F5E5A"


def draw_callout(x, y, text, color):
    """
    Draw a short callout with a white halo behind it.

    Lines often pass right behind a callout. Drawing a thick white copy of
    the text first, then the coloured text on top, keeps the words readable
    without moving them. (The paint-order attribute would be shorter, but
    some SVG renderers ignore it and the text disappears.)
    """
    safe_text = escape(text)
    halo = (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="12" text-anchor="middle" '
        f'fill="#FFFFFF" stroke="#FFFFFF" stroke-width="4" stroke-linejoin="round">'
        f'{safe_text}</text>'
    )
    label = (
        f'<text x="{x:.1f}" y="{y:.1f}" font-size="12" text-anchor="middle" '
        f'fill="{color}">{safe_text}</text>'
    )
    return halo + "\n" + label


def wrap_text(text, max_chars):
    """
    Break a long sentence into lines of at most max_chars, splitting on spaces.

    SVG text never wraps by itself, so long scope lines would run off the
    right edge without this.
    """
    words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        if current_line == "":
            candidate = word
        else:
            candidate = current_line + " " + word
        if len(candidate) <= max_chars:
            current_line = candidate
        else:
            if current_line != "":
                lines.append(current_line)
            current_line = word
    if current_line != "":
        lines.append(current_line)
    return lines


def clamp_score(value):
    """Keep scores inside the -2..+2 scale so a typo can't push a point off the canvas."""
    if value > 2:
        return 2.0
    if value < -2:
        return -2.0
    return float(value)


def draw_smiley(cx, cy, mood):
    """
    Draw one simple smiley as SVG.

    mood is one of: "ecstatic", "happy", "sad", "crying".
    Faces are built from basic shapes rather than emoji, because emoji
    render differently (or not at all) across viewers.
    """
    parts = []
    # Face outline
    parts.append(
        f'<circle cx="{cx}" cy="{cy}" r="12" fill="none" '
        f'stroke="{FACE_COLOR}" stroke-width="1.5"/>'
    )
    # Eyes
    parts.append(f'<circle cx="{cx - 4}" cy="{cy - 4}" r="1.5" fill="{FACE_COLOR}"/>')
    parts.append(f'<circle cx="{cx + 4}" cy="{cy - 4}" r="1.5" fill="{FACE_COLOR}"/>')

    # Mouth: an upward curve for happy faces, a downward curve for sad ones
    if mood == "ecstatic":
        # A filled open grin reads as "wow" more clearly than a bigger curve
        parts.append(
            f'<path d="M{cx - 6} {cy + 2} Q{cx} {cy + 10} {cx + 6} {cy + 2} Z" '
            f'fill="{FACE_COLOR}"/>'
        )
    elif mood == "happy":
        parts.append(
            f'<path d="M{cx - 5} {cy + 3} Q{cx} {cy + 8} {cx + 5} {cy + 3}" '
            f'fill="none" stroke="{FACE_COLOR}" stroke-width="1.5" stroke-linecap="round"/>'
        )
    else:
        parts.append(
            f'<path d="M{cx - 5} {cy + 7} Q{cx} {cy + 2} {cx + 5} {cy + 7}" '
            f'fill="none" stroke="{FACE_COLOR}" stroke-width="1.5" stroke-linecap="round"/>'
        )

    # Tears separate "crying" from merely "sad"
    if mood == "crying":
        parts.append(
            f'<path d="M{cx - 5} {cy - 1} L{cx - 6} {cy + 5}" '
            f'stroke="{FACE_COLOR}" stroke-width="1.5" stroke-linecap="round"/>'
        )
        parts.append(
            f'<path d="M{cx + 5} {cy - 1} L{cx + 6} {cy + 5}" '
            f'stroke="{FACE_COLOR}" stroke-width="1.5" stroke-linecap="round"/>'
        )

    return "\n".join(parts)


def build_pain_polygons(points):
    """
    Work out the red areas: every stretch where the journey is below neutral.

    points is a list of (x, y, score). Each red area is closed along the
    neutral line, so we add the exact spot where the line crosses neutral
    on the way down and on the way up. Without those crossing points the
    red shading would spill over into the happy parts of the curve.

    Returns a list of polygons, each a list of (x, y) pairs.
    """
    polygons = []
    current = []
    baseline_y = None

    # The neutral line's y is the same for every point; read it once from
    # the first point's geometry (score 0 sits at y + score * PX_PER_SCORE).
    first_x, first_y, first_score = points[0]
    baseline_y = first_y + first_score * PX_PER_SCORE

    for index in range(len(points)):
        x, y, score = points[index]
        is_below = score < 0

        if is_below:
            if len(current) == 0:
                # Starting a new red area. Begin it on the neutral line.
                if index == 0:
                    # The journey starts below neutral: anchor straight down from the first point.
                    current.append((x, baseline_y))
                else:
                    prev_x, prev_y, prev_score = points[index - 1]
                    crossing_x = find_crossing_x(prev_x, prev_score, x, score)
                    current.append((crossing_x, baseline_y))
            current.append((x, y))
        else:
            if len(current) > 0:
                # Leaving a red area. Close it where the line climbs back to neutral.
                prev_x, prev_y, prev_score = points[index - 1]
                crossing_x = find_crossing_x(prev_x, prev_score, x, score)
                current.append((crossing_x, baseline_y))
                polygons.append(current)
                current = []

    # If the journey ends below neutral (for example the user churned),
    # close the last red area straight up from the final point.
    if len(current) > 0:
        last_x, last_y, last_score = points[-1]
        current.append((last_x, baseline_y))
        polygons.append(current)

    return polygons


def find_crossing_x(x1, score1, x2, score2):
    """Find where a straight segment between two steps crosses neutral (score 0)."""
    if score2 == score1:
        # Flat segment: it can't cross, so just return the midpoint to stay safe
        return (x1 + x2) / 2
    fraction = (0 - score1) / (score2 - score1)
    return x1 + fraction * (x2 - x1)


def render(journey):
    """Turn the journey dictionary into a complete SVG string."""
    steps = journey["steps"]
    if len(steps) < 2:
        raise ValueError("A journey needs at least two steps to draw a line.")

    title = journey.get("title", "")

    # ----- Horizontal layout -----
    # Worked out first, because the width decides how the scope lines wrap.
    step_count = len(steps)
    first_step_x = AXIS_X + FIRST_STEP_GAP
    last_step_x = first_step_x + (step_count - 1) * STEP_SPACING
    width = int(last_step_x + RIGHT_PADDING)
    if width < MIN_WIDTH:
        width = MIN_WIDTH

    # ----- Scope lines at the top -----
    # A curve on its own doesn't say whose journey it is or what "good"
    # looks like. These lines make the scenario readable without the chat.
    max_chars_per_line = int((width - 60) / CHAR_WIDTH_12PX)
    scope_lines = []   # each item is (label_or_empty, text)
    for label, key in SCOPE_FIELDS:
        value = journey.get(key, "")
        if not value:
            continue
        wrapped = wrap_text(label + ": " + value, max_chars_per_line)
        for line_number in range(len(wrapped)):
            line = wrapped[line_number]
            if line_number == 0:
                # Split the bold label from the rest of the first line
                rest = line[len(label) + 1:]
                scope_lines.append((label + ":", rest))
            else:
                scope_lines.append(("", line))

    # ----- Vertical layout -----
    header_y = 32
    if title:
        header_y = header_y + 24
    scope_start_y = header_y
    header_y = header_y + len(scope_lines) * SCOPE_LINE_HEIGHT

    # Extra headroom so a "why" callout above a +2 peak stays on the canvas
    plot_top = header_y + 40

    baseline_y = plot_top + 2 * PX_PER_SCORE      # where score 0 sits
    plot_bottom = plot_top + 4 * PX_PER_SCORE     # where score -2 sits

    # Step labels are drawn vertically below the plot, like the hand-drawn maps.
    # Size that space from the longest label so nothing gets cut off.
    longest_label = 0
    for step in steps:
        if len(step["label"]) > longest_label:
            longest_label = len(step["label"])
    label_top = plot_bottom + 30
    label_height = longest_label * CHAR_WIDTH_12PX

    legend_y = label_top + label_height + 30
    height = int(legend_y + 30)

    # ----- Work out every point once, then reuse -----
    journey_points = []   # (x, y, score) for today's journey
    fix_points = []       # (x, y) for the green "with fixes" line
    for index in range(step_count):
        step = steps[index]
        x = first_step_x + index * STEP_SPACING
        score = clamp_score(step["score"])
        # Higher feeling means higher on screen, which means a smaller y
        y = baseline_y - score * PX_PER_SCORE
        journey_points.append((x, y, score))

        if "fix" in step and "fix_score" in step:
            fixed_score = clamp_score(step["fix_score"])
        else:
            fixed_score = score
        fix_y = baseline_y - fixed_score * PX_PER_SCORE
        fix_points.append((x, fix_y))

    svg = []
    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" font-family="Helvetica, Arial, sans-serif">'
    )
    # White background so the file reads well when opened or pasted anywhere
    svg.append(f'<rect x="0" y="0" width="{width}" height="{height}" fill="#FFFFFF"/>')
    svg.append(
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" '
        'markerWidth="6" markerHeight="6" orient="auto-start-reverse">'
        f'<path d="M2 1L8 5L2 9" fill="none" stroke="{AXIS_COLOR}" stroke-width="1.5"/>'
        '</marker></defs>'
    )

    # ----- Title and scope -----
    if title:
        svg.append(
            f'<text x="30" y="32" font-size="16" font-weight="bold" '
            f'fill="{TEXT_COLOR}">{escape(title)}</text>'
        )
    line_y = scope_start_y
    for label, text in scope_lines:
        if label:
            svg.append(
                f'<text x="30" y="{line_y}" font-size="12" fill="{MUTED_TEXT}">'
                f'<tspan font-weight="bold" fill="{TEXT_COLOR}">{escape(label)}</tspan>'
                f'{escape(text)}</text>'
            )
        else:
            svg.append(
                f'<text x="30" y="{line_y}" font-size="12" fill="{MUTED_TEXT}">{escape(text)}</text>'
            )
        line_y = line_y + SCOPE_LINE_HEIGHT

    # ----- Axes -----
    svg.append(
        f'<line x1="{AXIS_X}" y1="{plot_bottom + 15}" x2="{AXIS_X}" y2="{plot_top - 15}" '
        f'stroke="{AXIS_COLOR}" stroke-width="1" marker-end="url(#arrow)"/>'
    )
    svg.append(
        f'<line x1="{AXIS_X}" y1="{baseline_y}" x2="{width - 20}" y2="{baseline_y}" '
        f'stroke="{AXIS_COLOR}" stroke-width="1" marker-end="url(#arrow)"/>'
    )

    # ----- Smiley scale on the y-axis -----
    face_x = AXIS_X - 35
    svg.append(draw_smiley(face_x, baseline_y - 2 * PX_PER_SCORE, "ecstatic"))
    svg.append(draw_smiley(face_x, baseline_y - 1 * PX_PER_SCORE, "happy"))
    svg.append(draw_smiley(face_x, baseline_y + 1 * PX_PER_SCORE, "sad"))
    svg.append(draw_smiley(face_x, baseline_y + 2 * PX_PER_SCORE, "crying"))

    # ----- Red pain areas (drawn first so the lines sit on top) -----
    pain_polygons = build_pain_polygons(journey_points)
    for polygon in pain_polygons:
        point_strings = []
        for px, py in polygon:
            point_strings.append(f"{px:.1f},{py:.1f}")
        svg.append(
            f'<polygon points="{" ".join(point_strings)}" '
            f'fill="{PAIN_COLOR}" opacity="0.4"/>'
        )

    # ----- Green "with fixes" line (only if at least one fix exists) -----
    has_any_fix = False
    for step in steps:
        if "fix" in step:
            has_any_fix = True

    if has_any_fix:
        path_parts = []
        for index in range(len(fix_points)):
            fx, fy = fix_points[index]
            command = "M" if index == 0 else "L"
            path_parts.append(f"{command}{fx:.1f} {fy:.1f}")
        svg.append(
            f'<path d="{" ".join(path_parts)}" fill="none" stroke="{FIX_COLOR}" '
            f'stroke-width="2" stroke-dasharray="6 4"/>'
        )

    # ----- Purple journey line and its points -----
    path_parts = []
    for index in range(len(journey_points)):
        jx, jy, _score = journey_points[index]
        command = "M" if index == 0 else "L"
        path_parts.append(f"{command}{jx:.1f} {jy:.1f}")
    svg.append(
        f'<path d="{" ".join(path_parts)}" fill="none" stroke="{JOURNEY_COLOR}" stroke-width="2"/>'
    )
    for jx, jy, _score in journey_points:
        svg.append(f'<circle cx="{jx:.1f}" cy="{jy:.1f}" r="4" fill="{JOURNEY_COLOR}"/>')

    # ----- Callouts -----
    for index in range(step_count):
        step = steps[index]
        jx, jy, score = journey_points[index]

        # Delight reason sits just above the point it explains
        if "why" in step:
            svg.append(draw_callout(jx, jy - 12, step["why"], TEXT_COLOR))

        # Fix name sits just above the lifted green point, in green,
        # so it reads as "this is what pulls the dip up"
        if "fix" in step:
            fx, fy = fix_points[index]
            svg.append(
                f'<circle cx="{fx:.1f}" cy="{fy:.1f}" r="3.5" fill="{FIX_COLOR}"/>'
            )
            svg.append(draw_callout(fx, fy - 10, step["fix"], FIX_COLOR))

    # ----- Step labels, written vertically under each point -----
    # rotate(-90) turns the text to read bottom-to-top; text-anchor="end"
    # makes each label finish right under the plot, so all labels line up.
    for index in range(step_count):
        step = steps[index]
        jx, _jy, _score = journey_points[index]
        svg.append(
            f'<text x="{jx:.1f}" y="{label_top:.1f}" font-size="12" text-anchor="end" '
            f'fill="{TEXT_COLOR}" transform="rotate(-90 {jx:.1f} {label_top:.1f})" '
            f'dominant-baseline="central">{escape(step["label"])}</text>'
        )

    # ----- Legend -----
    legend_x = 30
    svg.append(
        f'<line x1="{legend_x}" y1="{legend_y}" x2="{legend_x + 24}" y2="{legend_y}" '
        f'stroke="{JOURNEY_COLOR}" stroke-width="2"/>'
    )
    svg.append(
        f'<text x="{legend_x + 30}" y="{legend_y + 4}" font-size="12" fill="{TEXT_COLOR}">Today</text>'
    )
    svg.append(
        f'<rect x="{legend_x + 90}" y="{legend_y - 6}" width="14" height="12" '
        f'fill="{PAIN_COLOR}" opacity="0.4"/>'
    )
    svg.append(
        f'<text x="{legend_x + 110}" y="{legend_y + 4}" font-size="12" fill="{TEXT_COLOR}">Pain</text>'
    )
    if has_any_fix:
        svg.append(
            f'<line x1="{legend_x + 160}" y1="{legend_y}" x2="{legend_x + 184}" y2="{legend_y}" '
            f'stroke="{FIX_COLOR}" stroke-width="2" stroke-dasharray="6 4"/>'
        )
        svg.append(
            f'<text x="{legend_x + 190}" y="{legend_y + 4}" font-size="12" '
            f'fill="{TEXT_COLOR}">With fixes</text>'
        )

    svg.append("</svg>")
    return "\n".join(svg)


def main():
    if len(sys.argv) != 3:
        print("Usage: python render_map.py journey.json journey.svg")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2]

    with open(input_path, "r", encoding="utf-8") as input_file:
        journey = json.load(input_file)

    svg_text = render(journey)

    with open(output_path, "w", encoding="utf-8") as output_file:
        output_file.write(svg_text)

    print(f"Map written to {output_path}")


if __name__ == "__main__":
    main()
