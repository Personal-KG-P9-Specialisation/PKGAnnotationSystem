import os
database = os.getenv('DATABASE') #triples
conv_file = os.getenv('conv_file')#./convs/conv.jsonl
patterns = os.getenv('agentJsonl')#agent_patterns.jsonl
dis_pattern = os.getenv('dis_pattern') #dis_pattern.jsonl

if __name__ == "__main__":
    relations = ['At_location', 'Desires', 'HasA','HasProperty','IsA','PartOf','MotivatedByGoal','Aversion_preference','has_name','has_age','has_gender', 'job_status', 'school_status','do']
    rel_text = ''
    for x in relations:
        rel_text += ',' + x
    rel_text = rel_text[1:]

    cmd = "python3 -m prodigy rel.manual "+database+" blank:en "+conv_file+" --label "+rel_text+" --span-label AGENT,ENTITY --wrap --add-ents --patterns agent_pattern.jsonl --disable-patterns "+dis_pattern
    os.system(cmd)
