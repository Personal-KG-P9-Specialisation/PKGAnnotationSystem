import os, json, difflib, copy
import pandas as pd
import time

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
#Process the personachat .txt files processed by ... into conversations usable by the triple annotations system
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

#Split the dataset into n lines long files
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


#Removes duplicate conversations from the path file from the path_anno files (annotated conversations in the DB)
def remove_duplicate(path, path_anno):
    dup_lst = list()
    w = open(path+'.bak','w')
    with open(path_anno,'r') as f:
        for idx,line in enumerate(f):
            conv = json.loads(line)
            dup_lst.append(conv['text'])
    path_f = open(path,'r')
    for idx,line in enumerate(path_f):
        c = json.loads(line)
        if c['text'] in dup_lst:
            print("Duplicate on lines {}".format(idx))
            continue
        w.write(json.dumps(c)+'\n')
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

#Creates candidates for subject/object mentions outputted for one conversation.
# Is used in TripleProcessor
class CandidateGenerator:
    def __init__(self,conceptnet_path='',entities=[]):
        self.conceptnet_path = conceptnet_path
        self.entities = entities
        if self.entities == []:
            self.entities = self.load_ConceptNet()


    #taken from our PKGAnalysis repository
    # Assumes conceptnet 5.5 / 5.7 source file in conceptnet folder
    def load_ConceptNet(self):
        # The graph is available at: https://github.com/commonsense/conceptnet5/wiki/Downloads
        # It will be downloaded as .csv but is tab-seperated
        df = pd.read_csv(self.conceptnet_path,sep='\t', error_bad_lines=False)
        node1s = set(df.iloc[:,2])
        node2s = set(df.iloc[:,3])
        nodes = list(node1s)
        nodes.extend(list(node2s))
        return list(set(nodes))

    #taken from our PKGAnalysis repository
    def entity_candidates(self, em, n=5, cutoff = 0.3):
        el_list = list()
        for e in self.entities:
            if em in str(e):
                el_list.append(e)
        el_list = difflib.get_close_matches(em,el_list, n=n, cutoff=cutoff)
        return [{'id':x} for x in el_list]
    
    #creates candidates for input conversation
    def candidatesFor(self,conv):
        lst_of_utt = []
        for i in range(len(conv['utterances'])):
            utts = self.create_candidate(conv['utterances'][i])
            lst_of_utt.extend(utts)
        return lst_of_utt

     
    def create_candidate(self, utt):
        phrases = utt['spans']
        lst_of_utt = []
        for i in range(len(phrases)):
            utt_copy = copy.deepcopy(utt)
            utt_copy['spans'] = [ phrases[i] ]
            #del utt_copy['relations'] #new addition
            utt_copy['options'] = self.entity_candidates(phrases[i]['text'])
            lst_of_utt.append(utt_copy)
        return lst_of_utt




#Processes the triple annotated data and makes it available for the other tasks.
class TripleProcessor:
    def __init__(self, data_path):
        self.data_convs = []
        self.data_path = data_path
        self.__load_data_path()
        self.convert_all_convs()

    def __load_data_path(self):
        data_json = []
        with open(self.data_path,'r') as f:
            for idx,line in enumerate(f):
                data_json.append( json.loads(line))
        self.data_convs = data_json

    def convert_all_convs(self):
        convs = []
        for x in self.data_convs:
            convs.append(self.convert_conv(x))
        self.data_convs = convs

    def convert_conv(self, conv):
        text = conv['text']
        utterances = text.split('\n')
        utterances = [{'text':x, 'span_text': [], 'relations':[], 'spans':[],'turn': None, 'conv_id':conv['conv_id']} for x in utterances]
        
        start = 0
        text_utt_map = {}
        for idx in range(len(utterances)):
            utterances[idx]['span_text'] = (start,start+len(utterances[idx]['text']))
            start += len(utterances[idx]['text'])

        relations = conv['relations']
        relations.sort(key=lambda x: x['head_span']['start']) 
        utt_id = 0
        for idx in range(len(relations)):
            conv_start, conv_end = utterances[utt_id]['span_text']

            #subject span of relation
            sub_span = relations[idx]['head_span']
            
            #iterates the utterance to match the current subject span. We assume that subject and object in the same utterance.
            while not (conv_start <= sub_span['start'] and sub_span['start'] < conv_end):
                utt_id +=1
                #print(conv['conv_id'])
                #print(utterances[utt_id]['span_text'], sub_span['start'],sub_span['end'], text[sub_span['start']:sub_span['end']])
                #print(utt_id, len(utterance))
                if len(utterances) == utt_id:
                    print("Something is wrong with Conversation with id : {}".format(conv['conv_id']))
                    return
                conv_start, conv_end = utterances[utt_id]['span_text']

            obj_span = relations[idx]['child_span']
            
            adj_rel = TripleProcessor.__create_relation__(text, utterances[utt_id], sub_span, obj_span, relations[idx]['label'])
            utterances[utt_id]['relations'].append(adj_rel)
            utterances[utt_id]['spans'].append(adj_rel['head_span'])
            utterances[utt_id]['spans'].append(adj_rel['child_span'])


        for idx, x in enumerate(utterances):
            del x['span_text']
            x['turn'] = idx
        """with open('entity_linking_sample2.jsonl','w') as f:
            for x in utterances:
                f.write(json.dumps(x)+'\n')"""
        return {'utterances' : utterances, 'conv_id': conv['conv_id']}
        

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

    def write_data(self, path):
        f = open(path,'w')
        for x in self.data_convs:
            f.write(json.dumps(x)+'\n')
    def __remove_rels_from_utt__(self, utt):
        del utt['relations']
        return utt
    def export_el_annotation_data(self, conceptnet_path, out_pointer):
        start = time.time()
        cg = CandidateGenerator(conceptnet_path=conceptnet_path)
        print("ConceptNet loaded after: {}s".format(str(time.time()-start)))
        counter = 0
        def remove_rels_from_utt(utt):
            del utt['relations']
            return utt
        def remove_zero_choice(utt):
            if len(utt['options']) == 0:
                return None
            return utt
        for conv in self.data_convs:
            utts = cg.candidatesFor(conv)
            for u in utts:
                counter += 1
                d = remove_rels_from_utt(u)
                d = remove_zero_choice(d)
                if d is None:
                    continue
                out_pointer.write(json.dumps(d)+'\n')
            print("Conversation ID {} finished after {}".format(conv['conv_id'], str(time.time()-start)))
        print("Utterances Writtes:\t{}\n".format(counter))
        print("Process finished after: {}s".format(str(time.time()-start)))
    #calculates the new indices og entity mentions for the utterances
    def __find_new_idx__(text, utt, rel_span):
        word = text[rel_span['start']:rel_span['end']]
        utt_word_s = utt['text'].find(word)
        utt_word_e = utt_word_s + len(word)
        return utt_word_s, utt_word_e


#Creates ids for convasations in input data to triple annotations interface
def create_ids(path, conv_id=0):
    f = open(path+'.bak','w')
    ff = open(path,'r')
    for idx, line in enumerate(ff):
        conv = json.loads(line)
        conv['conv_id'] = conv_id
        f.write(json.dumps(conv)+'\n')
        conv_id += 1


if __name__=="__main__":
    #ready for next string
    #create_ids('convs/convab.jsonl', 400)
    """for valid
    d= 'personachat/personachat_'
    combine_dataset(d+'train.jsonl',d+'valid.jsonl',d+'test.jsonl', d+'combined.jsonl')"""
    """p = 'convs' 
    c = ConversationProcessor(p)
    c.write_convs_to_jsonl("{}/conv.jsonl".format(p))"""
    c = TripleProcessor('/home/test/Github/PKGAnnotationSystem/annotations_data/a_trpl_filt.jsonl')
    f = open('sample.jsonl','w')
    c.export_el_annotation_data('/home/test/Github/PKGAnalysis/ConceptNet/conceptnet-assertions-5.7.0.csv',f)
    f.close()

    #c.write_data('el_sample3.jsonl')

    #remove_duplicate('convs/convab.jsonl', 'annotations_data/triple1.jsonl')
    #remove_duplicate('convs/convab.jsonl', 'annotations_data/triple1.jsonl')
    #c = DatasetSplitter("convs/conv.jsonl","annotations_data/triple1.jsonl", 20)
    #c.split_data(200)
