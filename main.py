import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--type', nargs='?', default='triples')
args = parser.parse_args()



if __name__ == "__main__":
    if args.type == 'triples':
        database = os.getenv('DATABASE') #triples
        conv_file = os.getenv('conv_file')#./convs/conv.jsonl
        patterns = os.getenv('agentJsonl')#agent_patterns.jsonl
        dis_pattern = os.getenv('dis_pattern') #dis_pattern.jsonl
        relations = ['HasNot','At_location', 'Desires', 'HasA','HasProperty','IsA','PartOf','MotivatedByGoal','Aversion_preference','has_name','has_age','has_gender', 'job_status', 'school_status','do']
        rel_text = ''
        for x in relations:
            rel_text += ',' + x
        rel_text = rel_text[1:]

        cmd = "python3 -m prodigy rel.manual "+database+" blank:en "+conv_file+" --label "+rel_text+" --span-label AGENT,ENTITY --wrap --add-ents --patterns agent_pattern.jsonl --disable-patterns "+dis_pattern
        os.system(cmd)
    elif args.type == 'CSKG_ents':
        db = os.getenv('DB')
        instructions = 'conceptnet_linking/concept_instructions.html'
        datafile = os.getenv('concept_data')
        cmd = "python3 -m prodigy entity_linker.manual "+db+" "+datafile+" -F conceptnet_linking/entity_linking.py"
        os.environ["PRODIGY_CONFIG_OVERRIDES"] = '{"instructions":"'+instructions+'"}'
        os.system(cmd)
    elif args.type == 'personal_ent':
        pass
