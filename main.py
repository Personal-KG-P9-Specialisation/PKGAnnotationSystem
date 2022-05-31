import os
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('--type', nargs='?', default='triples')
args = parser.parse_args()

#For running conceptnet entity linking interface
#export concept_data=annotations_data/conceptnet_input_divide/person10.jsonl DATABASE=conceptnet_entities PRODIGY_PORT=9010 && python3 -m main --type CSKG_ents

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
        db = os.getenv('DATABASE')
        instructions = 'conceptnet_linking/concept_instructions.html'
        datafile = os.getenv('concept_data')
        cmd = "python3 -m prodigy entity_linker.manual "+db+" "+datafile+" -F conceptnet_linking/entity_linking.py"
        os.environ["PRODIGY_CONFIG_OVERRIDES"] = '{"instructions":"'+instructions+'", "global_css": ".prodigy-button-reject { display: none } .prodigy-button-ignore { display: none }"}'
        os.system(cmd)
    elif args.type == 'personal_ent':
        db = os.getenv('DATABASE')
        instructions = 'personal_entity/personal_instructions.html'
        os.environ["PRODIGY_CONFIG_OVERRIDES"] = '{"instructions":"'+instructions+'"}'
        datafile = os.getenv('personal_data')
        dis_pattern = os.getenv('dis_pattern')

        cmd = f"python3 -m prodigy rel.manual {db} blank:en {datafile} --label COREF --span-label PERSONAL,AGENT --add-ents --wrap --patterns agent_pattern.jsonl --disable-patterns {dis_pattern}"
        os.system(cmd)
