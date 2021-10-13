FROM python:3.7
WORKDIR /web
ADD . /web
RUN pip install -r requirements.txt
RUN pip install opencv-python-headless
CMD python app.py