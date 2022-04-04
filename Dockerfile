FROM python:3.9.10-slim-buster
#WORKDIR /project
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt
COPY . .
CMD ["python3", "-m", "main.py"]
