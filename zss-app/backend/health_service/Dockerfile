FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5002

COPY DejaVuSans.ttf /usr/local/lib/python3.9/site-packages/fpdf/font/
COPY DejaVuSans-Bold.ttf /usr/local/lib/python3.9/site-packages/fpdf/font/

CMD ["python", "run.py"]