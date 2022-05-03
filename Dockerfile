FROM python:3.9.10-slim-buster
#WORKDIR /project
COPY prodigy_license.txt prodigy_license.txt
RUN pip3 install -r prodigy_license.txt
COPY . /conceptnet_linking/.
COPY preprocess.py preprocess.py
CMD ["python3", "-m", "prodigy", "entity_linker.manual", "concept_ents", "sample2.jsonl", "-F", "entity_linking.py"]
