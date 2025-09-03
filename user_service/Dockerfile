FROM python:3.13-alpine

ENV  PYTHONDONTWRITEBYTECODE=1

ENV PYTHONBUFFERED=1

WORKDIR /app

RUN pip install --upgrade pip

RUN apk add curl

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY entrypoint.sh ./entrypoint.sh
RUN sed -i "s/\r$//" entrypoint.sh && chmod +x entrypoint.sh

COPY . .

EXPOSE 8000

CMD [ "python", "manage.py", "runserver", "0.0.0.0:8000" ]

ENTRYPOINT ["./entrypoint.sh"]