"""
Custom Prodigy recipe to perform manual annotation of entity links
Run the following command in the directory to start server. Requires sample2.jsonl with option2 field.
python3 -m prodigy entity_linker.manual ents sample2.jsonl -F entity_linking.py
"""


import prodigy
from prodigy.components.loaders import TXT, JSONL
from prodigy.util import set_hashes
from prodigy.components.filters import filter_duplicates

from pathlib import Path


#python3 -m prodigy entity_linker.manual ents entity_linking_sample.jsonl -F entity_linking.py
#python3 -m prodigy entity_linker.manual ents sample2.jsonl -F entity_linking.py
@prodigy.recipe(
    "entity_linker.manual",
    dataset=("The dataset to use", "positional", None, str),
    source=("The source data as a .txt file", "positional", None, Path),
    #nlp_dir=("Path to the NLP model with a pretrained NER component", "positional", None, Path),
    #kb_loc=("Path to the KB", "positional", None, Path),
    #entity_loc=("Path to the file with additional information about the entities", "positional", None, Path),
)
def entity_linker_manual(dataset, source):#, nlp_dir, kb_loc, entity_loc):
    # Load the NLP and KB objects from file
    #nlp = spacy.load(nlp_dir)
    #kb = KnowledgeBase(vocab=nlp.vocab, entity_vector_length=1)
    #kb.load_bulk(kb_loc)
    #model = EntityRecognizer(nlp)

    # Read the pre-defined CSV file into dictionaries mapping QIDs to the full names and descriptions
    #id_dict = dict()
    #with entity_loc.open("r", encoding="utf8") as csvfile:
    #    csvreader = csv.reader(csvfile, delimiter=",")
    #    for row in csvreader:
    #        id_dict[row[0]] = (row[1], row[2])

    # Initialize the Prodigy stream by running the NER model
    stream = JSONL(source)
    #stream = [set_hashes(eg) for eg in stream]
    #stream = (eg for score, eg in model(stream))
    # For each NER mention, add the candidates from the KB to the annotation task
    #stream = _add_options(stream, kb, id_dict)
    stream = _create_options(stream)
    stream = [set_hashes(eg) for eg in stream]
    stream = filter_duplicates(stream, by_input=False, by_task=True)

    return {
        "dataset": dataset,
        "stream": stream,
        "view_id": "choice",
        "config": {"choice_auto_accept": False}
    }

#Method from tutorial
def _add_options(stream, kb, id_dict):
    """ Define the options the annotator will be given, by consulting the candidates from the KB for each NER span. """
    for task in stream:
        text = task["text"]
        for span in task["spans"]:
            start_char = int(span["start"])
            end_char = int(span["end"])
            mention = text[start_char:end_char]

            candidates = kb.get_candidates(mention)
            if candidates:
                options = [{"id": c.entity_, "html": _print_url(c.entity_, id_dict)} for c in candidates]

                # we sort the options by ID
                options = sorted(options, key=lambda r: int(r["id"][1:]))

                # we add in a few additional options in case a correct ID can not be picked
                options.append({"id": "NIL_otherLink", "text": "Link not in options"})
                options.append({"id": "NIL_ambiguous", "text": "Need more context"})

                task["options"] = options
                yield task

#convert to actual linkable stuff.
def _transform_options(stream):
    for task in stream:
        text = task["text"]
        options = task["options"]
        options = [{"id": c['id'], "text": c['id']} for c in options]
        options.append({"id": "NIL_otherLink", "text": "Entity not in options"})
        options.append({"id": "NIL_ambiguous", "text": "Need more context"})
        task["options"] = options
        yield task
import copy
#for optimised format
def _create_options(stream):
    for task in stream:
        for idx,span in enumerate(task["spans"]):
            start_char = int(span["start"])
            end_char = int(span["end"])
            mention = task['text'][start_char:end_char]
            if mention.lower() in ["my", "your","his", "her", "its", "our", "their", "i", "we"]:
                continue
            new_task = copy.deepcopy(task)
            if task['options2'][idx] != []:
                options = [{"id": c['id'], "html": _print_url(c['id'])} for c in task['options2'][idx]]
                options.append({"id": "NIL_otherLink", "text": "Entity not in options"})
                options.append({"id": "NIL_ambiguous", "text": "Need more context"})
                new_task["options"] = options
                new_task["spans"] = [span]
                yield new_task

#TODO: needs modification to Conceptnet instead.
def _print_url(entity_id):
    """ For each candidate QID, create a link to the corresponding Wikidata page and print the description """
    url_prefix = "https://conceptnet.io"
    option = "<p title='&#63 for more info'> "+entity_id.split('/')[-1] +" <a href='" + url_prefix + entity_id + "' target='_blank' style='float: right;padding-right: 30px;'>" + "<span>&#63;</span>" + "</a></p>"
    return option
