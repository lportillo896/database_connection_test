FROM python:3.11-buster
EXPOSE 5000

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["python", "app.py", "getroutes.py", "db_utils.py", "models.py"]