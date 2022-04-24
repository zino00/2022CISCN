import pickle

# pkl 得到 txt 文件


def pkl2txt(pkl_path, txt_path):
    with open(pkl_path, 'rb') as fin:
        list_sensitive_funcname = pickle.load(fin)
    with open(txt_path, 'w') as txt_file:
        for func_name in list_sensitive_funcname:
            txt_file.write(func_name + '\n')


if __name__ == '__main__':
    pkl2txt("/home/sung/Desktop/joern/script/data/sensitive_func.pkl",
            "/home/sung/Desktop/joern/script/sensitive_funcname.txt")
