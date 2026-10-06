# Built from the repo root (see docker-compose.yml) so the skill's render
# script can be copied in and reused for the review page's maps.
FROM python:3.12-slim

WORKDIR /app

COPY collector/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY collector/app.py /app/app.py
COPY customer-journey-map /app/customer-journey-map

EXPOSE 8000
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
