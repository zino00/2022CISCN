import os

all_bc_folder = 'bcfiles'
all_ll_folder = 'sliced_unlinked'
xml_path = "./manifest.xml"
ir2vec_path = "/home/yuhan/IR2Vec"
Vocab_path = '/vocabulary/seedEmbeddingVocab-300-llvm12.txt'
data_file_path = 'data_Juliet.txt'
label_file_path = 'label_Juliet.txt'
name_file_path = 'info_Juliet.txt'


def get_data_and_label():
    count0=0
    count1=0
    label_file = open(label_file_path, 'w')
    name_file = open(name_file_path, 'w')
    names = os.listdir(all_ll_folder)
    for name in names:
        # 相对路径
        ll_folder_path = os.path.join('%s/%s' % (all_ll_folder, name))
        var_lines = os.listdir(ll_folder_path)
        for var_line in var_lines:
            command = 'env LD_LIBRARY_PATH=. '+'opt-12 -enable-new-pm=0 '+'-load ../Tag/TagLabel.so -tag-label ' + \
                 ll_folder_path+'/'+var_line +' -o ' +ll_folder_path+'/'+var_line[:-3]+'-opt.bc'+\
                ' -selector getVulnInstID -xml-path '+xml_path+'> vul_line.txt'
            print(command)
            #os.system(command)
            var=var_line[:var_line.find('_')]
            line=var_line[var_line.find('_')+1:var_line.find('.')]
            # if line in dict[name]:
            #     class_num = '1'
            #     count1=count1+1
            # else:
            #     class_num = '0'
            #     count0=count0+1
            command = ir2vec_path+'/bin/ir2vec '+'-sym -vocab ' + \
                ir2vec_path+Vocab_path+' -o '+data_file_path + \
                ' -level p '+ll_folder_path+'/'+var_line
            name_file.write(name+'.c '+line+' '+var+'\n')
            label_file.write(class_num+'\n')
            print(command)
            os.system(command)
    name_file.close()
    label_file.close()
    print("0:"+str(count0)+' '+'1:'+str(count1))

if __name__ == "__main__":
    get_data_and_label()
