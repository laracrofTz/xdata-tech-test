FROM python:3.10-slim

# this prevents py from writing pyc files to disk, keping container clean
ENV PYTHONDONTWRITEBYTECODE 1
# forces python to flush output (for container logs purpose)
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y ffmpeg && \
    apt-get clean

COPY asr/ .

EXPOSE 8001

CMD ["gunicorn", "-w", "3", "--threads", "2", "-b", "0.0.0.0:8001", "asr_api:app", "--preload", "--timeout", "180"]
