FROM python:3.7
RUN mkdir /app
ADD . /app
WORKDIR /app
ENV PYTHONUNBUFFERED=0
RUN apt install gcc && pip3 install -r requirements.txt
ENTRYPOINT ["python", "-u", "app.py"]
