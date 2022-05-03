# c文件目录路径
src_dir_path = "/home/yuhan/桌面/SARD_C/000"
# 工作所在文件夹的路径
work_dir_path = '/home/yuhan/桌面/SARD_C'

# Joern 运行的 .sc 脚本
SC_path = '/home/yuhan/桌面/2022CISCN/slice/cpg_extract.sc'
# txt 文件路径 包含敏感函数名
sensitive_funcname_txt_path = "/home/yuhan/桌面/2022CISCN/slice/sensitive_funcname.txt"
# c文件编译依赖的目录路径，不存在则为''
support_dir_path = ''
# llvm的安装路径
llvm_build = '/usr/lib/llvm-12'
# dg工具的路径
dg_tools_path = '/home/yuhan/dg/tools'

# 数据集提供的含漏洞信息的xml文件
xml_path = "/home/yuhan/桌面/SARD_C/SARD_testcaseinfo.xml"
# IR2Vec的路径
ir2vec_path = "/home/yuhan/桌面/2022CISCN/IR2Vec"
# 相对于IR2Vec目录的嵌入词汇表位置
Vocab_path = '/vocabulary/seedEmbeddingVocab-300-llvm12.txt'

#ir与c文件对应关系字典的路径
bc_c_dict_path=work_dir_path+'/bc_c_dict.pkl'
# 漏洞字典的路径
vul_candidate_func_path = work_dir_path+'/vul_candidate_func.pkl'
vul_candidate_var_path = work_dir_path+'/vul_candidate_var.pkl'
# 错误命令的路径
error_command_file_path = work_dir_path+'/error.txt'

# 未连接bc文件目录的路径
unlinked_bc_dir_path = work_dir_path+'/unlinked_bcfile'
# 连接后bc文件目录的路径
bc_dir_path = work_dir_path+'/bcfile'
# 切片所在目录
slice_dir_path = work_dir_path+'/slice_file'

# 单个标签文件所在目录
label_dir_path = work_dir_path+'/label_file'
# 单个向量文件所在目录
data_dir_path = work_dir_path+'/data_file'
#切片-标签映射的字典文件路径
slice_to_label_file_path = work_dir_path+'/slice_to_label_file_path.pkl'
#向量文件路径
data_file_path = work_dir_path+'/data_SARD.txt'
#标签文件路径
label_file_path = work_dir_path+'/label_SARD.txt'
#切片信息文件路径
info_file_path = work_dir_path+'/info_SARD.txt'
#保存切片路径的文件路径
ll_path_file_path = work_dir_path+'/ll_path_SARD.txt'
