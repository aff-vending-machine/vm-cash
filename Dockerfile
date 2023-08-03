FROM arm64v8/python:3.7-alpine

WORKDIR /app

COPY . .

RUN apk add --no-cache bash tzdata nano

RUN cp /usr/share/zoneinfo/Asia/Bangkok /etc/localtime

RUN python3 -m pip install -r requirements.txt

RUN cp -r -f /usr/share/zoneinfo/Asia/Bangkok /etc/localtime

CMD ["gunicorn", "-b", ":8080", "main:api", "-w", "2"]
