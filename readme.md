# Personal Knowledge Graph Annotation Interfaces and Processing

## Requirements
- git LFS
- Prodigy License

## Personal entities
First create input data for personal entity annotation system by:
```
python3 -m preprocess --option personal_entity --input annotations_data/filtered_annotated_triples.jsonl --output annotations_data/personal_entity_input.jsonl
```

## Relations Check Interface
We observe that the current HasProperty relation is too generic. Therefore, we seperate the HasProperty relation into HasValue when the object of a triple refers to a string literal. To run the interface, execute the following commands:
````
docker build -f relation_check/Dockerfile -t rel_check:1 .
docker run -it --rm -e conv_path=/project/annotations_data/filtered_annotated_triples.jsonl -e triple_path=/project/annotations_data/updated_filtered_relation_annotated_triples.jsonl -v "$(pwd)"/annotations_data/.:/project/annotations_data rel_check:1
```
conv_path should point to filtered_annotated_triples.jsonl
triple path is where the output will be stored. The output of our pass over the data is in updated_filtered_annotated_triples.jsonl