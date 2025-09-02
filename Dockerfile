FROM python:3.12-slim

# Everything will be done in /app (Not in the main OS Image)
WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=app.py

CMD ["flask", "run"]