FROM python:3.9.10-slim-buster
WORKDIR /project
RUN pip3 install pandas
RUN mkdir /project/relation_check
COPY ./relation_check/ /project/relation_check/.
COPY preprocess.py /project/preprocess.py
CMD ["python3", "-m", "relation_check.relation_check_interface"]
