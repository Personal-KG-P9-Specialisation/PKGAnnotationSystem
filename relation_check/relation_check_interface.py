import os
from preprocess import TripleProcessor
import json

class AnnotationInterface(TripleProcessor):
    def __init__(self, conv_path):
        super().__init__(conv_path)
    
    #Show an utterance and one HasProperty relation in a conversation and give option for pressing 'v'
    # depending on if the relation should change to HasValue. 
    def interface(self, file_pointer):
        def snap_input_to_bool(value: str):
            if value == 'v':
                return True
            return False
        def read_processed_convs():
            conv_ids = []
            for line in file_pointer:
                if line == '':
                    continue
                conv_ids.append(json.loads(line)['conv_id'])
            return conv_ids
        
        conv_ids = read_processed_convs()
        for conv in self.data_convs:
            if conv['conv_id'] in conv_ids:
                continue
            print(f"Current conversation: {conv['conv_id']} \n")
            new_utterances = []
            for utt in conv['utterances']:
                #new_rels = []
                for rel in utt['relations']:
                    if rel['label'] == 'HasProperty' or rel['label'] == 'IsA':
                        print(f"Utterance text: {utt['text']}\n")
                        sbj = rel['head_span'] 
                        sbj_text = utt['text'][sbj['start'] : sbj['end']]
                        obj = rel['child_span']
                        obj_text = utt['text'][obj['start'] : obj['end']]
                        print(f"Subject: {sbj_text}, Predicate: {rel['label']}, Object:  {obj_text}\n")
                        change = snap_input_to_bool(input())
                        if change:
                            rel['label'] = 'HasValue'
                        #new_rels.append(rel)
                    #else:
                        #new_rels.append(rel)
                new_utterances.append(utt)
            file_pointer.write(json.dumps({"conv_id": conv['conv_id'], "utterances": new_utterances}) + '\n')

if __name__ == "__main__":
    conv_path = os.getenv('conv_path')
    triple_path = os.getenv('triple_path')
    #conv_path = '/home/test/Github/PKGAnnotationSystem/annotations_data/filtered_annotated_triples.jsonl'
    c = AnnotationInterface(conv_path)
    #triple_path = '/home/test/Github/PKGAnnotationSystem/annotations_data/updated_filtered_relation_annotated_triples.jsonl'
    f = open(triple_path,'r+')
    c.interface(f)
    f.close()