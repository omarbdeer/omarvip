FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

COPY . .

ENV SECRET_KEY=build-time-key
ENV DEBUG=False
ENV ALLOWED_HOSTS=*

RUN python manage.py collectstatic --noinput

EXPOSE 8080

CMD ["sh", "startup.sh"]
