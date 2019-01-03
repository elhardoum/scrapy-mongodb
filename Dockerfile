FROM python:3

RUN [ -d /app ] || mkdir /app

WORKDIR /app

COPY src .

RUN pip install -r requirements.txt

CMD [ "sleep", "infinity" ]
