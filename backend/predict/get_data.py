import os
import path_required

# IR2Vec的路径
ir2vec_path = path_required.ir2vec_path
# 相对于IR2Vec目录的嵌入词汇表位置
Vocab_path = path_required.Vocab_path


def run_ir2vec(single_dir_path):
    # 切片所在目录
    slice_dir_path = single_dir_path+'/slice_file'
    # 单个向量文件所在目录
    data_dir_path = single_dir_path+'/data_file'
    #向量文件路径
    data_file_path = single_dir_path+'/data.txt'
    #保存切片路径的文件路径
    ll_path_file_path = single_dir_path+'/ll_path.txt'
    data_file = open(data_file_path, 'w+')
    ll_path_file = open(ll_path_file_path, 'w+')
    slice_dirs = os.listdir(slice_dir_path)
    if os.path.exists(data_dir_path) == 0:
        os.mkdir(data_dir_path)
    for slice_dir in slice_dirs:
        slice_child_dir_path = os.path.join(
            '%s/%s' % (slice_dir_path, slice_dir))
        slice_names = os.listdir(slice_child_dir_path)
        for slice_name in slice_names:
            # 该切片的绝对路径
            slice_path = slice_child_dir_path+'/'+slice_name
            # ir2vec词嵌入
            single_data_dir_path = data_dir_path+'/'+slice_dir
            single_data_file_path = single_data_dir_path+'/'+slice_name+'_lable.txt'
            if os.path.exists(single_data_dir_path) == 0:
                os.mkdir(single_data_dir_path)
            if os.path.exists(single_data_file_path) == 0:
                command = ir2vec_path+'/build/bin/ir2vec '+'-fa -vocab ' + ir2vec_path+Vocab_path + \
                    ' -o '+single_data_file_path + ' -level f '+slice_path
                # print(command)
                os.system(command)
            command = "cat "+single_data_file_path+" >> "+data_file_path
            # print(command)
            os.system(command)
            command = "echo \"##########" + "\" >> "+data_file_path
            os.system(command)
            # 存绝对路径
            ll_path_file.write(slice_path+'\n')
    ll_path_file.close()
    data_file.close()
    return data_file_path
