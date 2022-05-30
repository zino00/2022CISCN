import os
from tqdm import tqdm
import numpy as np
from keras import Model, models
from path_required import project_path, tag_path
import path_required
import json
import pickle

def loadData(datapath):
    irLine = []  # 每行ir向量
    irList = []  # ir切片向量列表
    print('Data processing progress:')
    # 打开文件：以二进制读模式、utf-8格式的编码方式打开
    with tqdm(total=os.path.getsize(datapath)) as pbar:
        with open(datapath, 'r', encoding='utf-8') as frData:
            for line in frData:
                pbar.update(len(line))
                # 逐行遍历：行内字段按'\t'分隔符分隔，转换为列表
                line = line.strip()
                a = line.split('\t')
                if '#' not in a[0]:
                    a = list(map(float, a))
                    irLine.append(a)
                else:
                    x = [0 for i in range(300)]
                    while len(irLine) < 1000:
                        irLine.append(x)
                    irList.append(irLine)
                    irLine = []
                    continue
    return np.array(irList)


def get_predict_line(value_sequence, threshold_value=0.5):
    value_sequence = list(value_sequence)
    vs = len(value_sequence) - 1
    while value_sequence[vs] == value_sequence[-1]:
        vs -= 1
    value_sequence = value_sequence[:vs + 2]

    predict_line = []
    for i in range(len(value_sequence)):
        if value_sequence[i] > threshold_value:
            predict_line.append(i)
    return predict_line


def model_predict(model, datapath):
    data = loadData(datapath)
    partial_model = Model(
        inputs=model.layers[0].input, outputs=model.layers[7].output)
    output_test = partial_model([data], training=False)
    # print(output_test)
    # print(output_test.shape)
    predict_line = []
    for j in range(output_test.shape[0]):
        predict_line.append(get_predict_line(output_test[j]))
    return predict_line


def run_BRNN(single_dir_path):
    # 向量文件路径
    data_file_path = single_dir_path+"/data.txt"
    modelPath = project_path+"/predict/model/model_10-0.97.h5"
    model = models.load_model(modelPath)
    # print("ready to run BRNN to predict")
    result_line = model_predict(model, data_file_path)
    print(result_line)
    return result_line


def result_process(single_dir_path, result_line):
    # ir与c文件对应关系字典的路径
    bc_c_dict_path = single_dir_path+'/bc_c_dict.pkl'
    bc_c_dict=pickle.load(open(bc_c_dict_path, 'rb'))
    src_file_path=path_required.src_dir_path
    ll_path_file_path = single_dir_path+"/ll_path.txt"
    ll_path_file = open(ll_path_file_path, "rb")
    ll_paths = ll_path_file.readlines()
    for i in range(len(ll_paths)):
        ll_paths[i]=ll_paths[i].decode('utf-8').strip()
    tmp_file_path = single_dir_path + "/tmp.txt"
    # C文件和其绝对路径的映射
    basename_path={}
    # C文件和漏洞行号的映射
    vul = {}
    for i in range(len(result_line)):
        for id in result_line[i]:
            command = tag_path+"/build/IRHandler " + \
                str(ll_paths[i])+' --selector=printTargetInst --id=' + \
                str(id) + ">" + tmp_file_path
            print(command)
            os.system(command)
            with open(tmp_file_path, "r") as file:
                info = file.readline() 
                basename, line = info.split(': ')[1].strip().split(':')
                if basename not in vul:
                    vul[basename] = []
                vul[basename].append(line)
                absolute_path=ll_paths[i].replace("/slice_file/","/C_file/")
                absolute_path=absolute_path[:absolute_path.rfind('/')]+'/'+basename
                basename_path[basename]=absolute_path
    command = "rm " + tmp_file_path
    os.system(command)
    result_list = []
    result_item = {}
    for basename in vul:
        lines = vul[basename]
        absolute_path=basename_path[basename]
        result_item["path"] = absolute_path[absolute_path.find(single_dir_path):]
        with open(absolute_path, "r") as C_file:
            result_item["code"] = C_file.read()
        result_item["vul"] = lines
        result_list.append(result_item)
    return json.dumps(result_list)


def get_result(single_dir_path):
    return result_process(single_dir_path, run_BRNN(single_dir_path))

