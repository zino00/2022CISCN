# 项目文件夹的路径
project_path="/home/yuhan/桌面/2022CISCN/backend"
# 保存全部文件的文件夹路径
work_dir_path = '/home/yuhan/fuck'
# 保存单个文件的文件夹路径
single_dir_path = ''
# c文件编译依赖的目录路径，不存在则为''
support_dir_path = '/home/yuhan/桌面/Juliet/C/testcasesupport'
# llvm的安装路径
llvm_build = '/usr/lib/llvm-12'
# dg工具的路径
dg_tools_path = '/home/yuhan/dg/tools'
# c文件目录路径
src_dir_path = ""
'''
以下路径若无特殊需要，不必修改
'''
# tag工具文件夹的路径
tag_path=project_path+'/tag'
# IR2Vec的相对路径
ir2vec_path = project_path+"/IR2Vec"
# 相对于IR2Vec目录的嵌入词汇表位置
Vocab_path = '/vocabulary/seedEmbeddingVocab-300-llvm12.txt'
# Joern 运行的 .sc 脚本的相对路径
SC_path = project_path+'/predict/cpg_extract.sc'
# txt 文件路径 包含敏感函数名
sensitive_funcname_txt_path = project_path+"/predict/sensitive_funcname.txt"


# 设置c文件路径
def set_src_dir_path(path):
    global src_dir_path
    src_dir_path=path
    return src_dir_path
# 设置单次上传对应文件路径
def set_single_dir_path(filename):
    global single_dir_path
    single_dir_path =work_dir_path+'/'+filename
    return single_dir_path

