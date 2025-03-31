FROM python:3.10-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN SECRET_KEY="temporary-build-key" python manage.py collectstatic --noinput

EXPOSE 8000

ENV PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=website.settings \
    PORT=8000

CMD waitress-serve --port=$PORT --host=0.0.0.0 website.wsgi:application
