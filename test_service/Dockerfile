FROM python:3.13-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONBUFFERED=1

WORKDIR /app

RUN apk add curl

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY entrypoint.sh ./entrypoint.sh

COPY . .

RUN sed -i "s/\r$//" entrypoint.sh && chmod +x entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]

CMD ["python", "service_test.py"]

