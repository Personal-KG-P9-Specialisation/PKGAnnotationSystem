FROM python:3.9.10-slim-buster
#WORKDIR /project
RUN pip3 install -r 
COPY . /relation_check/.
COPY preprocess.py preprocess.py
CMD ["python3", "-m", "relation_check.relation_check_interface"]