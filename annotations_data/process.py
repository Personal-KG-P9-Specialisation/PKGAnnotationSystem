import json

def duplicate_check(path):
    data_w_n = list()
    f = open(path,'r')
    for idx,line in enumerate(f):
        j_line = json.loads(line)
        data_w_n.append(j_line['text'])
    len_data = len(data_w_n)

    print("Data with Duplicate is {}\nData without Duplicate is {}".format(len_data, len(set(data_w_n))))
def check_ids(path_anno):
    conv_ids = []
    with open(path_anno,'r') as f:
        for l in f:
            conv_id = json.loads(l)['conv_id']
            conv_ids.append(conv_id)
    print("Data with Duplicate is {}\nData without Duplicate is {}".format(len(conv_ids), len(set(conv_ids))))

if __name__ == "__main__":
    check_ids("temp/april5_trpl.jsonl.bak")

