# Official Python image use kar rahe hain
FROM python:3.10-slim

# Environment variables set karna taaki Python output buffer na kare
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Container ke andar working directory set kar rahe hain
WORKDIR /app

# Requirements file copy karke dependencies install karna
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Baaki saara backend code copy kar rahe hain
COPY . /app/

# Port 8080 expose kar rahe hain (jo aap apne server ke liye use kar rahe hain)
EXPOSE 8080

# Server start karne ki command
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8080", "--workers", "3"]
