import os
if __name__ == "__main__":
    relations = ['At_location', 'Desires', 'HasA','HasProperty','IsA','PartOf','MotivatedByGoal','Aversion_preference','has_name','has_age','has_gender']
    rel_reduce = lambda x,y: x+' '+y
    rel_text = ''
    for x in relations:
        rel_text += ',' + x
    rel_text = rel_text[1:]

    cmd = "python3 -m prodigy rel.manual triples blank:en ./convs/conv.jsonl --label "+rel_text+" --span-label AGENT --wrap --add-ents --patterns agent_pattern.jsonl"
    os.system(cmd)
