'''
Author: Sung
Date: 2022-04-24 11:58
LastEditors: Sung
LastEditTime: 2022-04-24 12:05
FilePath: \2022CISCN\slice\get_vul_linenumber.py
Description: 得到可能的漏洞行号
Copyright (c) 2022 by Sung, All Rights Reserved. 
'''
from operator import itemgetter
import subprocess
import os
import time
import tqdm
import json
import re
# C file folder path
C_source_dir = "/home/sung/Desktop/joern/Juliet_Test_Suite_v1.3_for_C_Cpp/C/testcases/"
# .sc script path
SC_path = '/home/sung/Desktop/joern/script/cpg_extract.sc'
# cpg.bin file path
CPG_source_path = './data/parsed/cpg/'
# all properties json file path
Json_source_path = './data/parsed/json/'
# result json path
Res_source_path = './data/parsed/res/'
# sensittive function name txt file path
sensitive_funcname_txt_path = "/home/sung/Desktop/joern/script/sensitive_funcname.txt"


def c2cpg(c_File_Path, cpg_Path):
    # parse source code into cpg
    print('parsing source code into cpg...')
    for filepath, dirnames, filenames in os.walk(c_File_Path):
        for item in filenames:
            print(item)
            if item[-2:] == '.c':
                print("start")
                filename = item[:-2] + '.bin'
                shell_command = "joern-parse --output " + filename + " " + c_File_Path + item
                subprocess.call(shell_command, shell=True)
                # move cpg into cpg dir
                shell_command = "mv -b ./" + filename + " " + cpg_Path
                subprocess.call(shell_command, shell=True)


def cpg2json(cpg_folder_Path, json_folder_Path, sc_path=SC_path):
    print('json')
    for filepath, dirnames, filenames in os.walk(cpg_folder_Path):
        for item in filenames:
            print(item)
            filename = item[:-4] + '.json'
            cpg_Path = cpg_folder_Path + '/' + item
            project_Path = item[:-4] + ".bin"
            shell_command = "joern --script " + sc_path + " --params cpgFile=" + \
                cpg_Path + ",projectFolder=" + project_Path + \
                ",outFile=" + json_folder_Path + filename
            subprocess.call(shell_command, shell=True)


def get_all_function_list(txt_path):
    function_list = []
    with open(txt_path, 'r') as txtfile:
        sensitive_funcname = txtfile.readline()
        function_list.append(sensitive_funcname)
    return function_list


def extract_properties(json_folder_path, result_folder_path, function_list):
    print('result')
    for filepath, dirnames, filenames in os.walk(json_folder_path):
        for item in filenames:
            print(item)
            with open(json_folder_path + item) as file:
                properties_data = json.load(file)
            with open(result_folder_path + item, 'w') as result:
                allres = []
                variable_list = []
                for item in properties_data:
                    if item['_label'] == "LOCAL":
                        variable_list.append(item['name'])
                for item in properties_data:
                    if '*' in item['code'] or '[' in item['code']:
                        res = {}
                        res['name'] = item['name']
                        res['lineNumber'] = item['lineNumber']
                        allres.append(res)
                        print(res)
                    elif '<operator>.assignment' == item['name'] and variable_list.count(re.split('=|\+|\-', item['code'])[1]) != 0:
                        res = {}
                        res['code'] = re.split('=', item['code'])[0]
                        res['lineNumber'] = item['lineNumber']
                        allres.append(res)
                        print(res)
                    elif function_list.count(item['name']) != 0:
                        res = {}
                        res['name'] = item['name']
                        res['lineNumber'] = item['lineNumber']
                        allres.append(res)
                        print(res)
                print(allres)
                json.dump(allres, result)


def all_c2cpg():
    dirs = os.listdir(C_source_dir)
    for c_folder in tqdm.tqdm(dirs):
        c_file_path = C_source_dir + c_folder
        cpg_path = CPG_source_path + c_folder
        os.makedirs(cpg_path)
        print(f'starting to parse {c_file_path}')
        c2cpg(c_file_path, cpg_path)


def all_cpg2json():
    dirs = os.listdir(CPG_source_path)
    for cpg_folder in tqdm.tqdm(dirs):
        cpg_folder_path = CPG_source_path + cpg_folder
        json_path = Json_source_path + cpg_folder + '/'
        os.makedirs(json_path)
        cpg2json(cpg_folder_path, json_path)


def all_extract_properties():
    dirs = os.listdir(Json_source_path)
    function_list = get_all_function_list(sensitive_funcname_txt_path)
    for json_folder in tqdm.tqdm(dirs):
        json_folder_path = Json_source_path + json_folder
        result_folder_path = Res_source_path + json_folder + '/'
        os.makedirs(result_folder_path)
        extract_properties(json_folder_path, result_folder_path, function_list)


if __name__ == "__main__":
    start = time.time()
    function_list = get_all_function_list(sensitive_funcname_txt_path)
    c2cpg(C_source_dir + "CWE15_External_Control_of_System_or_Configuration_Setting/",
          CPG_source_path)
    cpg2json(CPG_source_path,
             Json_source_path,
             SC_path)
    extract_properties(Json_source_path,
                       Res_source_path,
                       function_list)
    # all_c2cpg()
    # all_cpg2json()
    # all_extract_properties()
    end = time.time()
    print("循环运行时间:%.2f秒" % (end-start))
