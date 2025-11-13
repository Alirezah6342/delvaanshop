FROM python:3.12-alpine3.22

ENV PATH="/opt/venv/bin:$PATH"
RUN apk update && apk add --no-cache postgresql-client libjpeg zlib curl && rm -rf /var/cache/apk/*

RUN addgroup app && adduser -S -G app app

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

RUN chown app:app /app
USER app

COPY . .
RUN mkdir -p /app/media/app/staticfiles
EXPOSE 8000

CMD ["sh", "-c", "python manage.py collectstatic --noinput && python manage.py runserver 0.0.0.0:8000"]

