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
                return False
            return True
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
                new_rels = []
                for rel in utt['relations']:
                    if rel['label'] == 'HasProperty':
                        print(f"Utterance text: {utt['text']}\n")
                        sbj = rel['head_span'] 
                        sbj_text = utt['text'][sbj['start'] : sbj['end']]
                        obj = rel['child_span']
                        obj_text = utt['text'][obj['start'] : obj['end']]
                        print(f"Subject: {sbj_text}, Predicate: {rel['label']}, Object:  {obj_text}\n")
                        change = snap_input_to_bool(input())
                        if change:
                            rel['label'] = 'HasValue'
                        new_rels.append(rel)
                    else:
                        new_rels.append(rel)
                new_utterances.append(utt)
            file_pointer.write(json.dumps({"conv_id": conv['conv_id'], "utterances": new_utterances}) + '\n')

if __name__ == "__main__":
    conv_path = '/home/test/Github/PKGAnnotationSystem/annotations_data/temp/april5_filt_trpl.jsonl'
    c = AnnotationInterface(conv_path)
    f = open('/home/test/Github/PKGAnnotationSystem/temp.jsonl','r+')
    c.interface(f)
    f.close()