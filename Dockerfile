FROM python:3.9

RUN useradd iceranking

WORKDIR /home/iceranking

COPY requirements.txt requirements.txt
RUN python -m venv venv

RUN apt-get update && apt-get -y install gcc libffi-dev

RUN venv/bin/pip install -r requirements.txt

RUN venv/bin/pip install gunicorn

COPY app app
COPY migrations migrations
COPY icecompass.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP app

RUN chown -R iceranking:iceranking ./
USER iceranking

EXPOSE 5050
ENTRYPOINT ["./boot.sh"]