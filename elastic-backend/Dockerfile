FROM python:3.10-slim

WORKDIR /app

COPY cv-index.py ./cv-index.py
COPY cv-valid-dev.csv ./cv-valid-dev.csv

RUN pip install --no-cache-dir elasticsearch pandas

CMD ["python", "cv-index.py"]
