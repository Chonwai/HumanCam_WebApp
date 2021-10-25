FROM python:3.7
WORKDIR /web
ADD . /web

RUN apt-get update
RUN pip install -r requirements.txt
RUN pip install opencv-python-headless

# Setup supervisord
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY gunicorn.conf /etc/supervisor/gunicorn.conf

COPY . .

# CMD ["supervisord", "-c", "supervisord.conf"]
# CMD ["gunicorn", "app:app", "-c", "./gunicorn.conf"]
# CMD ["supervisord"]
ENTRYPOINT ["bash", "entrypoint.sh"]