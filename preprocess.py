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
		o = {'text': conversation}
		return json.dumps(o)



		

class ConversationProcessor:
	def __init__(self, path:str):
		self.conv_files = ["{}/{}".format(path,x) for x in os.listdir(path) if x.endswith('.txt')]
		self.convs = [self.__create_conversation(x) for x in self.conv_files]

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
		




if __name__=="__main__":
	
	c = ConversationProcessor(p)
	c.write_convs_to_jsonl("{}/conv.jsonl".format(p))
