FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Passed in by Jenkins: --build-arg APP_VERSION=42 --build-arg GIT_SHA=abc1234
ARG APP_VERSION=dev
ARG GIT_SHA=local
ENV APP_VERSION=$APP_VERSION GIT_SHA=$GIT_SHA

EXPOSE 5000
CMD ["python", "app.py"]
