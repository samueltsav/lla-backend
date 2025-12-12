FROM python:3.14-alpine

ENV  PYTHONDONTWRITEBYTECODE=1

ENV PYTHONBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip

RUN apk update && \
    apk add --no-cache curl gcc musl-dev python3-dev libffi-dev

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

RUN sed -i "s/\r$//" entrypoint.sh && chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]