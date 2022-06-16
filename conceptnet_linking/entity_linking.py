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
)
def entity_linker_manual(dataset, source):

    # Initialize the Prodigy stream by running the NER model
    stream = JSONL(source)
    stream = _create_options(stream)
    stream = [set_hashes(eg) for eg in stream]
    stream = filter_duplicates(stream, by_input=False, by_task=True)

    return {
        "dataset": dataset,
        "stream": stream,
        "view_id": "choice",
        "config": {"choice_auto_accept": False}
    }

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
            if mention.lower() in ["my", "your","his", "her", "its", "our", "their", "i", "we", "he", "she", "it"]:
                continue
            new_task = copy.deepcopy(task)
            if task['options2'][idx] != []:
                options = [{"id": c['id'], "html": _print_url(c['id'])} for c in task['options2'][idx]]
                options.append({"id": "NIL_otherLink", "text": "Entity not in options"})
                options.append({"id": "NIL_ambiguous", "text": "Need more context"})
                new_task["options"] = options
                new_task["spans"] = [span]
                yield new_task


def process_entity_id(em):
    splits = em.split('/')
    if splits[-1] in ['v','n']:
        return splits[-2]
    return splits[-1]

def _print_url(entity_id):
    url_prefix = "https://conceptnet.io"
    option = "<p title='&#63 for more info'> "+process_entity_id(entity_id) +" <a href='" + url_prefix + entity_id + "' target='_blank' style='float: right;padding-right: 30px;'>" + "<span>&#63;</span>" + "</a></p>"
    return option
