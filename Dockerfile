FROM python:3.9.12-slim-buster
ENV STATIC_URL /static
ENV STATIC_PATH /var/www/app/static
RUN pip install --upgrade pip
COPY ./requirements.txt /var/www/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /var/www/requirements.txt

COPY ./app /app
EXPOSE 5000
CMD [ "python", "/app/app.py" ]