FROM python:3.7-slim
WORKDIR /app_back
COPY requirements.txt .
RUN pip3 install -r requirements.txt --no-cache-dir
COPY . .
#CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
CMD python manage.py migrate && \
    python manage.py collectstatic --no-input && \
    gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000
