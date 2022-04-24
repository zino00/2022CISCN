'''
Author: Sung
Date: 2022-04-24 11:59
LastEditors: Sung
LastEditTime: 2022-04-24 12:04
FilePath: \2022CISCN\slice\get_sensitive_funcname.py
Description: 通过反序列化 sensitive_func.pkl 得到 sensitive_funcname.txt 敏感函数名
Copyright (c) 2022 by Sung, All Rights Reserved. 
'''
import pickle


def pkl2txt(pkl_path, sc_path):
    with open(pkl_path, 'rb') as fin:
        list_sensitive_funcname = pickle.load(fin)
    with open(sc_path, 'w') as txt_file:
        for func_name in list_sensitive_funcname:
            txt_file.write(func_name + '\n')


if __name__ == '__main__':
    pkl2txt("/home/sung/Desktop/joern/script/data/sensitive_func.pkl",
            "/home/sung/Desktop/joern/script/sensitive_funcname.txt")
