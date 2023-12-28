FROM python:3.11-alpine
LABEL mainteiner="katya.zadorozhna.00@gmail.com"

RUN mkdir /app

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

WORKDIR .

CMD gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind=0.0.0.0:8000
