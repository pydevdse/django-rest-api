FROM python:3.8
WORKDIR /app
COPY requirements.txt /app
RUN pip install --upgrade pip && pip install -r requirements.txt 
COPY . /app
EXPOSE 6000
ENTRYPOINT ["python", "docker-entrypoint.py"]
