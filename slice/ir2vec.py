import os
import pickle
import path_required

# IR2Vec的路径
ir2vec_path = path_required.ir2vec_path
# 相对于IR2Vec目录的嵌入词汇表位置
Vocab_path = path_required.Vocab_path
# 数据集提供的含漏洞信息的xml文件
xml_path = path_required.xml_path
# 切片所在目录
slice_dir_path = path_required.slice_dir_path
# 单个标签文件所在目录
label_dir_path = path_required.label_dir_path
# 单个向量文件所在目录
data_dir_path = path_required.data_dir_path
# 切片-标签映射的字典文件路径
slice_to_label_file_path = path_required.slice_to_label_file_path
# C文件-漏洞行号的字典文件路径
vuln_info_path = path_required.vuln_info_path
# 向量文件路径
data_file_path = path_required.data_file_path
# 标签文件路径
label_file_path = path_required.label_file_path
# 切片信息文件路径
info_file_path = path_required.info_file_path
# 保存切片路径的文件路径
ll_path_file_path = path_required.ll_path_file_path
# 需要数据集的大小
max_num = 200000


def get_data_and_label(get_data, get_label):
    # 切片-标签文件映射
    if os.path.exists(slice_to_label_file_path):
        slice_to_label = pickle.load(open(slice_to_label_file_path, 'rb'))
    else:
        slice_to_label = {}
    count = 0
    count_invalid = 0
    count0 = 0
    count1 = 0
    label_file = open(label_file_path, 'w+')
    info_file = open(info_file_path, 'w+')
    data_file = open(data_file_path, 'w+')
    ll_path_file = open(ll_path_file_path, 'w+')
    slice_dirs = os.listdir(slice_dir_path)
    if os.path.exists(label_dir_path) == 0:
        command = "mkdir "+label_dir_path
        os.system(command)
    if os.path.exists(data_dir_path) == 0:
        command = "mkdir "+data_dir_path
        os.system(command)
    for slice_dir in slice_dirs:
        slice_child_dir_path = os.path.join(
            '%s/%s' % (slice_dir_path, slice_dir))
        slice_names = os.listdir(slice_child_dir_path)
        for slice_name in slice_names:
            # 该切片相对于所有切片所在目录的路径
            slice_relative_path = slice_dir+'/'+slice_name
            count += 1
            print(count)
            # 该切片的绝对路径
            slice_path = slice_child_dir_path+'/'+slice_name
            # 打标签
            if get_label == 1:
                single_label_dir_path = label_dir_path+'/'+slice_dir
                single_label_file_path = single_label_dir_path+'/'+slice_name+'_lable.txt'
                if os.path.exists(vuln_info_path) == 0:
                    command = "./tag/build/IRHandler "+slice_path + \
                        " --selector=getVulnInstID-saveVulnInfo --xml-path=" + \
                        xml_path+' --vuln-info-path='+vuln_info_path
                    print(command)
                    os.system(command)
                if os.path.exists(single_label_dir_path) == 0:
                    command = "mkdir "+single_label_dir_path
                    os.system(command)
                if os.path.exists(single_label_file_path) == 0:
                    command = "./tag/build/IRHandler "+slice_path + \
                        ' --selector=getVulnInstID-useVulnInfo --vuln-info-path=' + \
                        vuln_info_path+' >> '+single_label_file_path
                    print(command)
                    os.system(command)
                if slice_relative_path not in slice_to_label:
                    slice_to_label[slice_relative_path] = []
                    if os.path.getsize(single_label_file_path) == 0:
                        # 没有漏洞
                        slice_to_label[slice_relative_path].append('0')
                        count0 += 1
                    else:
                        with open(single_label_file_path, "r") as single_lable_file:
                            labels = single_lable_file.readline().split('\t')
                            if '0' in labels or '999999999' in labels:
                                # 无效切片
                                slice_to_label[slice_relative_path].append('#')
                            else:
                                # 有漏洞
                                slice_to_label[slice_relative_path] = labels
                labels = slice_to_label[slice_relative_path]
                with open(slice_to_label_file_path, 'wb') as file:
                    pickle.dump(slice_to_label, file)
                if '#' not in labels:
                    for i in labels:
                        label_file.write(i+'\t')
                label_file.write('\n')
                if '0' in labels:
                    count0 += 1
                elif '#' in labels:
                    count_invalid += 1
                else:
                    count1 += 1
            # ir2vec词嵌入
            if get_data == 1:
                single_data_dir_path = data_dir_path+'/'+slice_dir
                single_data_file_path = single_data_dir_path+'/'+slice_name+'_lable.txt'
                if os.path.exists(single_data_dir_path) == 0:
                    command = "mkdir "+single_data_dir_path
                    os.system(command)
                if os.path.exists(single_data_file_path) == 0:
                    command = ir2vec_path+'/build/bin/ir2vec '+'-fa -vocab ' + ir2vec_path+Vocab_path + \
                        ' -o '+single_data_file_path + ' -level f '+slice_path
                    # print(command)
                    os.system(command)
                command = "cat "+single_data_file_path+" >> "+data_file_path
                print(command)
                os.system(command)
                command = "echo \"##########" + \
                    str(count)+"\" >> "+data_file_path
                os.system(command)
            # 存信息
            if slice_name.find('_') >= 0 and len(slice_name.split('_')) > 2:
                var = slice_name.split('_')[0]
                line = slice_name.split('_')[1]
                func = slice_name.split('_')[2]
                func = func[:func.find('.')]
                info_file.write(slice_dir+'.ll '+'variable:' +
                                var+' line:'+line+' loacted funcation:'+func+'\n')
            else:
                func_in = var = slice_name.split('_')[0]
                func = slice_name.split('_')[1]
                func = func[:func.find('.')]
                info_file.write(slice_dir+'.ll '+'funcation:' +
                                func_in+' located funcation:'+func+'\n')
            # 存绝对路径
            ll_path_file.write(slice_path+'\n')

            if count >= max_num:
                break

        if count >= max_num:
            break
    ll_path_file.close()
    info_file.close()
    label_file.close()
    data_file.close()
    return count, count0, count1, count_invalid


if __name__ == "__main__":
    print(get_data_and_label(1, 0))

