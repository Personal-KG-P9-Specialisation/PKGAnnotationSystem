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




if __name__=="__main__":
    pass
    """for valid
    d= 'personachat/personachat_'
    combine_dataset(d+'train.jsonl',d+'valid.jsonl',d+'test.jsonl', d+'combined.jsonl')"""
    p = 'convs' 
    c = ConversationProcessor(p)
    c.write_convs_to_jsonl("{}/conv.jsonl".format(p))
