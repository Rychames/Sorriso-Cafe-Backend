FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Definir variáveis temporárias para o collectstatic
RUN SECRET_KEY="temporary-build-key" \
    EMAIL_HOST_USER="temp@example.com" \
    EMAIL_HOST_PASSWORD="temp-password" \
    python manage.py collectstatic --noinput

EXPOSE 8000

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=website.settings \
    PORT=8000

CMD waitress-serve --port=${PORT:-8000} --host=0.0.0.0 website.wsgi:application
