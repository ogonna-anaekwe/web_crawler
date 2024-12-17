FROM python:3.11

ARG DIR=/web_crawler

ENV PYTHONPATH=${DIR}

WORKDIR ${DIR}

ADD . .

RUN pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["tail", "-f", "/dev/null"]