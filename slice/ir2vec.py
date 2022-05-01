import os
# 切片所在目录
slice_dir_path = '/home/yuhan/桌面/Juliet/C/slice_file'
# 单个标签文件所在目录
label_dir_path = '/home/yuhan/桌面/Juliet/C/label_file'
# 数据集提供的含漏洞信息的xml文件
xml_path = "/home/yuhan/桌面/Juliet/C/manifest.xml"
# IR2Vec的路径
ir2vec_path = "/home/yuhan/桌面/2022CISCN/IR2Vec"
# 相对于IR2Vec目录的嵌入词汇表位置
Vocab_path = '/vocabulary/seedEmbeddingVocab-300-llvm12.txt'

data_file_path = '/home/yuhan/桌面/Juliet/C/data_Juliet2.txt'
label_file_path = '/home/yuhan/桌面/Juliet/C/label_Juliet2.txt'
info_file_path = '/home/yuhan/桌面/Juliet/C/info_Juliet2.txt'
ll_path_file_path = '/home/yuhan/桌面/Juliet/C/ll_path_Juliet2.txt'

max_num=1000000

def get_data_and_label(get_data, get_label):
    count = 0
    label_file = open(label_file_path, 'w+')
    info_file = open(info_file_path, 'w+')
    data_file = open(data_file_path, 'w+')
    ll_path_file = open(ll_path_file_path, 'w+')
    slice_dirs = os.listdir(slice_dir_path)
    if os.path.exists(label_dir_path) == 0:
        command = "mkdir "+label_dir_path
        os.system(command)
    for slice_dir in slice_dirs:
        slice_child_dir_path = os.path.join(
            '%s/%s' % (slice_dir_path, slice_dir))
        slice_names = os.listdir(slice_child_dir_path)
        for slice_name in slice_names:
            count += 1
            slice_path = slice_child_dir_path+'/'+slice_name
            # 打标签
            if get_label == 1:
                single_label_dir_path = label_dir_path+'/'+slice_dir
                single_label_file_path = single_label_dir_path+'/'+slice_name+'_lable.txt'
                if os.path.exists(single_label_dir_path) == 0:
                    command = "mkdir "+single_label_dir_path
                    os.system(command)
                if os.path.exists(single_label_file_path) == 0:
                    command = "./tag/build/IRHandler "+slice_path + \
                        ' --selector=getVulnInstID --xml-path='+xml_path+' >> '+single_label_file_path
                    os.system(command)
                if os.path.getsize(single_label_file_path) == 0:
                    command = "echo 0 >> "+label_file_path
                    print(command)
                    os.system(command)
                else:
                    command = "cat "+single_label_file_path+" >> "+label_file_path
                    print(command)
                    os.system(command)
                    # 换行
                    command = "echo >> "+label_file_path
                    print(command)
                    os.system(command)
            # ir2vec词嵌入
            if get_data == 1:
                command = ir2vec_path+'/build/bin/ir2vec '+'-fa -vocab ' + ir2vec_path+Vocab_path + \
                    ' -o '+data_file_path + ' -level f '+slice_path
                # print(command)
                os.system(command)
                command = "echo \"##########"+str(count)+"\" >> "+data_file_path
                os.system(command)
            # 存信息
            if slice_name.find('_') >= 0:
                var = slice_name.split('_')[0]
                line = slice_name.split('_')[1]
                func = slice_name.split('_')[2]
                func = func[:func.find('.')]
                info_file.write(slice_dir+'.ll '+'variable:' +
                                var+' line:'+line+' func:'+func+'\n')
            else:
                func = slice_name[:slice_name.find('.')]
                info_file.write(slice_dir+'.ll '+'function:'+func+'\n')
            # 存路径
            ll_path_file.write(slice_path+'\n')
            
            if count >= max_num:
                break
        if count >= max_num:
            break
    ll_path_file.close()
    info_file.close()
    label_file.close()
    data_file.close()
    return count


if __name__ == "__main__":
    print(get_data_and_label(1, 1))
