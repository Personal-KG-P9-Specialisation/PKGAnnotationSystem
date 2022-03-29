import os, json

#Class for representing a conversation
class Conversation:
    def __init__(self, utterances: list):
        self.agent1_utterances = list()
        self.agent2_utterances = list()
        
        agent1 = True
        utterances = [x for x in utterances if x != '']

        for x in utterances:
            if agent1:
                self.agent1_utterances.append(x)
                agent1 = False
            else:
                self.agent2_utterances.append(x)
                agent1 = True

    #Converts a conversations to json format required by the triple annotator.
    def to_triple_json_str(self):
        conversation = ""
        assert len(self.agent1_utterances) == len(self.agent2_utterances), "No equal amount of utterances"
        for i in range(0,len(self.agent1_utterances)):
            
            conversation = conversation + "Agent 1: {}\n Agent 2: {}\n" \
                   .format(self.agent1_utterances[i], \
                   self.agent2_utterances[i])

        o = {'text': conversation[:-1]}
        return json.dumps(o)

class ConversationProcessor:
    def __init__(self, path:str):
        self.conv_files = ConversationProcessor.order_conv_files(path)
        self.convs = [self.__create_conversation(x) for x in self.conv_files]
    
    def order_conv_files(path):
        rank_cmp = lambda rank: int(rank.split('/')[-1].split('c')[0])
        files =sorted( ["{}/{}".format(path,x) for x in os.listdir(path) if x.endswith('.txt')], key=rank_cmp, reverse=True)
        return files
    def __create_conversation(self, path):
        data = None
        with open(path, 'r') as f:
            data = f.read()
        data = data.split('\n')
        return Conversation(data)
    
    def write_convs_to_jsonl(self, output_path):
        f = open(output_path, 'w')
        for c in self.convs:
            f.write(c.to_triple_json_str())
            f.write('\n')
        f.close()

class DatasetSplitter:
    def __init__(self, src_path, loaded_data_path, n_chars):
        self.path = src_path
        self.ldp = loaded_data_path
        self.n_chars = n_chars
        self.__load_dublicate_check_lst()

    def __load_dublicate_check_lst(self):
        f = open(self.ldp, 'r')
        self.duplicate_lst = list()
        for idx, line in enumerate(f):
            conv = json.loads(line)
            self.duplicate_lst.append(conv['text'][:self.n_chars])
        f.close()
    def format_write_path(self,partition_no):
        splits = self.path.split('.')
        return splits[0]+str(partition_no)+'.'+splits[1]

    def split_data(self, sample_size):
        f = open(self.path, 'r')
        w = open(self.format_write_path(1),'w')
        for idx,line in enumerate(f):
            conv = json.loads(line)
            if conv['text'][:self.n_chars] in self.duplicate_lst:
                continue
            if idx % sample_size == 0:
                w.close()
                file_path = self.format_write_path(idx)
                print("Switching Handle to: {}".format(file_path))
                w = open(file_path,'w')
            w.write(json.dumps(conv)+'\n')
        w.close()


def remove_duplicate(path, path_anno):
    dup_lst = list()
    w = open(path+'.bak','w')
    with open(path_anno,'r') as f:
        for idx,line in enumerate(f):
            conv = json.loads(line)
            dup_lst.append(conv['text'][:20])
    path_f = open(path,'r')
    for idx,line in enumerate(path_f):
        c = json.loads(line)
        if c['text'][:20] in dup_lst:
            print("Duplicate on lines {}".format(idx))
            continue
        w.write(line+'\n')
    path_f.close()
    w.close()

#combing the personachat datafiles into a single souce
def combine_dataset(path1, path2, path3, output_path):
    f = open(output_path,'w')
    with open(path1, 'r') as f1:
        lines = f1.readlines()
        f.writelines(lines)
    with open(path2, 'r') as f1:
        lines = f1.readlines()
        f.writelines(lines)
    with open(path3, 'r') as f1:
        f.writelines(f1.readlines())
    f.close()

class TripleProcessor:
    def __init__(self, data_path):
        self.data_path = data_path
        self.__load_data_path()
        self.convert_conv(self.data_convs[0], 0)

    def __load_data_path(self):
        data_json = []
        with open(self.data_path,'r') as f:
            for idx,line in enumerate(f):
                data_json.append( json.loads(line))
        self.data_convs = data_json

    def convert_conv(self, conv, conv_id):
        text = conv['text']
        utterances = text.split('\n')
        utterances = [{'text':x, 'span_text': [], 'relations':[], 'spans':[], 'conv_id':conv_id} for x in utterances]
        
        start = 0
        text_utt_map = {}
        for idx in range(len(utterances)):
            utterances[idx]['span_text'] = (start,start+len(utterances[idx]['text']))
            start += len(utterances[idx]['text'])

        relations = conv['relations']
        
        utt_id = 0
        for idx in range(len(relations)):
            conv_start, conv_end = utterances[utt_id]['span_text']
            sub_span = relations[idx]['head_span']
            while not (conv_start < sub_span['start'] and sub_span['start'] < conv_end):
                utt_id +=1
                conv_start, conv_end = utterances[utt_id]['span_text']

            obj_span = relations[idx]['child_span']
            
            adj_rel = TripleProcessor.__create_relation__(text, utterances[utt_id], sub_span, obj_span, relations[idx]['label'])
            utterances[utt_id]['relations'].append(adj_rel)
            utterances[utt_id]['spans'].append(adj_rel['head_span'])
            utterances[utt_id]['spans'].append(adj_rel['child_span'])

        for x in utterances:
            del x['span_text']
        """with open('entity_linking_sample2.jsonl','w') as f:
            for x in utterances:
                f.write(json.dumps(x)+'\n')"""
        return utterances
        

    def __create_entity_mention__(text, utt, rel_span):
        word_s, word_e = TripleProcessor.__find_new_idx__(text, utt, rel_span)
        return {'text': utt['text'][word_s:word_e], 'start':word_s ,'end':word_e,'label':"ENTITY" }
    
    def __create_relation__(text, utt, sub, obj, rel_text):
        relation = {
                    'head_span': TripleProcessor.__create_entity_mention__(text,utt,sub),
                    'child_span' : TripleProcessor.__create_entity_mention__(text,utt,obj),
                    'label':rel_text
        }
        return relation

    #calculates the new indices og entity mentions for the utterances
    def __find_new_idx__(text, utt, rel_span):
        word = text[rel_span['start']:rel_span['end']]
        utt_word_s = utt['text'].find(word)
        utt_word_e = utt_word_s + len(word)
        return utt_word_s, utt_word_e




if __name__=="__main__":
    pass
    """for valid
    d= 'personachat/personachat_'
    combine_dataset(d+'train.jsonl',d+'valid.jsonl',d+'test.jsonl', d+'combined.jsonl')"""
    """p = 'convs' 
    c = ConversationProcessor(p)
    c.write_convs_to_jsonl("{}/conv.jsonl".format(p))"""
    c = TripleProcessor('entity_linking_sample.jsonl')
    #remove_duplicate('convs/convaa.jsonl', 'annotations_data/triple1.jsonl')
    #c = DatasetSplitter("convs/conv.jsonl","annotations_data/triple1.jsonl", 20)
    #c.split_data(200)