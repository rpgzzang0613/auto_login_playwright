FROM mcr.microsoft.com/playwright/python:v1.54.0-noble

WORKDIR /app

# Linux 환경에서 CAPTCHA OCR을 수행하기 위해 Tesseract 설치
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-eng && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "main.py"]
