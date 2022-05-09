import os
import json
import pickle
import tag.readModuleInfoXML
import tag.readCallInfoXML
import get_vul_linenumber
import path_required
import multiprocessing
# c文件目录路径
src_dir_path = path_required.src_dir_path
# txt 文件路径 包含敏感函数名
sensitive_funcname_txt_path = path_required.sensitive_funcname_txt_path
# c文件编译依赖的目录路径，不存在则为''
support_dir_path = path_required.support_dir_path
# llvm的安装路径
llvm_build = path_required.llvm_build

# 工作所在文件夹的路径
work_dir_path = path_required.work_dir_path
# 漏洞字典的路径
vul_candidate_func_path = path_required.vul_candidate_func_path
vul_candidate_var_path = path_required.vul_candidate_var_path

# ir与c文件对应关系字典的路径
bc_c_dict_path = path_required.bc_c_dict_path

# 错误命令的路径
error_command_file_path = path_required.error_command_file_path
# dg工具的路径
dg_tools_path = path_required.dg_tools_path
# 未连接bc文件目录的路径
unlinked_bc_dir_path = path_required.unlinked_bc_dir_path
# 连接后bc文件目录的路径
bc_dir_path = path_required.bc_dir_path
# 切片结果目录的路径
slice_dir_path = path_required.slice_dir_path
# key:连接后的bc名, value:由被连接bc对应c文件名构成的列表 --由link生成
bc_c_dict = {}

# dir_name:当前所在文件夹，dir_path:被遍历目录的路径，result_dir_name：结果所在的目录名


def generate_bc():
     # 若不存在bc文件保存的路径,则创建
    if os.path.exists(unlinked_bc_dir_path) == 0:
        os.mkdir(unlinked_bc_dir_path)
    for current_filepath, src_dirnames, filenames in os.walk(src_dir_path):
        for filename in filenames:
            if filename[-2:] != '.c' and filename[-4:] != '.cpp':
                continue
            src_filename = filename
            # src_filenames = os.listdir(current_filepath+'/'+src_dirname)
            # # 若目录下不是文件,是目录,则跳过
            # if len(src_filenames) > 0 and os.path.isdir(current_filepath+'/'+src_dirname+'/'+src_filenames[0]) > 0:
            #     continue
            # 结果子目录名与c文件的完全相同
            unlinked_bc_child_dir_name = current_filepath[current_filepath.find(
                src_dir_path)+len(src_dir_path):]
            unlinked_bc_child_dir_path = unlinked_bc_dir_path+'/'+unlinked_bc_child_dir_name
            # 若不存在bc文件保存的子目录,则创建
            mkdir = unlinked_bc_dir_path
            for dir_name in unlinked_bc_child_dir_name.split('/'):
                mkdir += '/'+dir_name
                if os.path.exists(mkdir) == 0:
                    os.mkdir(mkdir)
            # 对于c文件，转化为IR
            file_name = src_filename[:src_filename.find('.')]
            # 编译命令
            command = llvm_build+'/bin/clang -c -g' + ' -emit-llvm -Xclang -disable-O0-optnone ' + \
                current_filepath+'/'+src_filename+' -o ' + \
                unlinked_bc_child_dir_path + '/' + file_name + '.bc'
            if support_dir_path != '':
                command = command+' -I '+support_dir_path
            # print(command)
            os.system(command)
            # 若编译失败，则删除所有文件
            if os.path.exists(unlinked_bc_child_dir_path + '/' + file_name + '.bc') == 0:
                command = 'rm '+current_filepath+'/'+src_filename
                os.system(command)
                command = 'rm -rf '+unlinked_bc_child_dir_path
                os.system(command)
                break
    # 删除空文件夹
    command = 'rmdir '+src_dir_path+'/* ; rmdir '+unlinked_bc_dir_path+'/*'
    os.system(command)
    print(command)

def link():
    '''
    连接,在get_vul_candidate()中调用
    '''
    # 创建连接后的bc所在文件夹
    if os.path.exists(bc_dir_path) == 0:
        command = 'mkdir '+bc_dir_path
        os.system(command)
    for current_filepath, unlinked_bc_child_dirnames, filenames in os.walk(unlinked_bc_dir_path):
        for unlinked_bc_child_dirname in unlinked_bc_child_dirnames:
            unlinked_bc_child_dir_path = current_filepath+'/'+unlinked_bc_child_dirname
            unlinked_bc_names = os.listdir(unlinked_bc_child_dir_path)
            # 若目录下不是bc文件,是目录,则跳过
            if len(unlinked_bc_names) > 0 and os.path.isdir(unlinked_bc_child_dir_path+'/'+unlinked_bc_names[0]):
                continue
            # 未连接的bc相对于所有bc文件所在目录的路径
            unlinked_bc_relative_path = unlinked_bc_child_dir_path[unlinked_bc_child_dir_path.find(
                unlinked_bc_dir_path)+len(unlinked_bc_dir_path):]
            # 连接后的bc名（一个文件不连接）
            if len(unlinked_bc_names) > 1:
                bc_name = unlinked_bc_relative_path[1:].replace('/', '_')+'.bc'
            elif len(unlinked_bc_names) == 1:
                bc_name = unlinked_bc_names[0]
            command = llvm_build+"/bin/llvm-link "
            bc_c_dict[bc_name] = []
            # 若有main_linux.bc存在,则不需要连接main.bc
            main_linux_exist = 0
            for unlinked_bc_name in unlinked_bc_names:
                if unlinked_bc_name == "main_linux.bc":
                    main_linux_exist = 1
                    break
            # 遍历为连接的bc,更新command,并保存c文件相对于所有c文件所在目录的路径
            for unlinked_bc_name in unlinked_bc_names:
                if main_linux_exist == 1 and unlinked_bc_name == "main.bc":
                    continue
                if unlinked_bc_name[0:4] == "main":
                    c_name = unlinked_bc_name[:-3]+".cpp"
                else:
                    c_name = unlinked_bc_name[:-3]+".c"
                bc_c_dict[bc_name].append(unlinked_bc_relative_path+'/'+c_name)
                command = command+unlinked_bc_child_dir_path+'/'+unlinked_bc_name+" "
            command = command+"-o "+bc_dir_path+'/'+bc_name
            # 若已存在连接后的bc,则不执行连接命令
            if os.path.exists(bc_dir_path+'/'+bc_name) > 0:
                continue
            # 确认有至少2个文件存在,执行连接
            if len(unlinked_bc_names) > 1:
                print(bc_dir_path+'/'+bc_name)
                os.system(command)
            elif len(unlinked_bc_names) == 1:
                command = "mv "+unlinked_bc_child_dir_path + \
                    '/' + bc_name+" " + bc_dir_path+'/'+bc_name
                print(command)
                os.system(command)
    with open(bc_c_dict_path, 'wb') as file:
        pickle.dump(bc_c_dict, file)

def get_single_bc_vul_candicate(bc_name, function_list, mutex):
    # # 线程池
    # p = Pool(len(bc_c_dict[bc_name]))
    # async_results=[]
    # # 遍历该bc文件对应的c文件 -- 获取漏洞候选的json
    # for c_path in bc_c_dict[bc_name]:
    #     async_results.append(p.apply_async(get_vul_linenumber.c2res, args=(c_path, function_list)))
    # p.close()
    # p.join()
    vul_json_file_paths = []
    for c_path in bc_c_dict[bc_name]:
        vul_json_file_paths.append(
            get_vul_linenumber.c2res(c_path, function_list))
    # for res in async_results:
    #     vul_json_file_paths.append(res.get())
    # #对含漏洞候选的pkl文件上锁
    mutex.acquire()
    # 加载已保存的漏洞候选映射（在生成json过程中可能会有所改动）
    if os.path.exists(vul_candidate_func_path):
        vul_candidate_func = pickle.load(open(vul_candidate_func_path, 'rb'))
    else:
        vul_candidate_func = {}
    if os.path.exists(vul_candidate_var_path):
        vul_candidate_var = pickle.load(open(vul_candidate_var_path, 'rb'))
    else:
        vul_candidate_var = {}
    vul_candidate_func[bc_name] = {}
    vul_candidate_var[bc_name] = {}
    for vul_json_file_path in vul_json_file_paths:
        vul_json_file = open(vul_json_file_path)
        print(vul_json_file)
        vul_json = json.load(vul_json_file)
        # 遍历漏洞候选的定位
        for name_line in vul_json:
            line = name_line['lineNumber']
            if 'function' in name_line:
                func = name_line['function']
                if func not in vul_candidate_func[bc_name]:
                    vul_candidate_func[bc_name][func] = []
                vul_candidate_func[bc_name][func].append(line)
            elif 'variable' in name_line or 'assignment' in name_line:
                if 'variable' in name_line:
                    var = name_line['variable']
                else:
                    var = name_line['assignment']
                if var not in vul_candidate_var[bc_name]:
                    vul_candidate_var[bc_name][var] = []
                vul_candidate_var[bc_name][var].append(line)
    # 每对一个bc文件提取漏洞候选后，保存候选漏洞的字典为pkl文件
    with open(vul_candidate_func_path, 'wb') as file:
        pickle.dump(vul_candidate_func, file)
    with open(vul_candidate_var_path, 'wb') as file:
        pickle.dump(vul_candidate_var, file)
    # 删掉joern 保存的 workspace 目录
    command = "rm -rf ./workspace"
    os.system(command)
    mutex.release()


def get_vul_candidate():
    '''
    得到每个bc文件的漏洞候选,在run_dg()中被调用
    '''
    # 得到bc文件-c文件的映射
    link() 
    # 得到敏感函数列表 function_list
    function_list = get_vul_linenumber.get_all_function_list(
        sensitive_funcname_txt_path)
    # 遍历bc文件夹中的bc文件
    bc_names = os.listdir(bc_dir_path)
    # (bc_name,function,linenumber{})的映射
    vul_candidate_func = {}
    # (bc_name,variable,linenumber{})的映射
    vul_candidate_var = {}
    # 加载已保存的漏洞候选映射
    if os.path.exists(vul_candidate_func_path):
        vul_candidate_func = pickle.load(open(vul_candidate_func_path, 'rb'))
    if os.path.exists(vul_candidate_var_path):
        vul_candidate_var = pickle.load(open(vul_candidate_var_path, 'rb'))
    print(len(vul_candidate_func))
    # 遍历bc文件,得到漏洞候选（线程池）
    p2 = multiprocessing.Pool(8)
    async_results = []
    mutex = multiprocessing.Manager().Lock()
    count = 0
    for bc_name in bc_names:
        # 不是bc文件，则跳过
        if bc_name[-2:] != 'bc':
            continue
        # 若bc文件已处理，则跳过
        if bc_name in vul_candidate_func.keys() and bc_name in vul_candidate_var.keys():
            continue
        count += 1
        print(count)
        async_results.append(p2.apply_async(get_single_bc_vul_candicate, args=(bc_name, function_list, mutex)))
    p2.close()
    p2.join()
    vul_candidate_func = pickle.load(open(vul_candidate_func_path, 'rb'))
    vul_candidate_var = pickle.load(open(vul_candidate_var_path, 'rb'))
    return vul_candidate_func, vul_candidate_var


def run_dg():
    count = 0
    # if os.path.exists(vul_candidate_func_path):
    #     vul_candidate_func = pickle.load(open(vul_candidate_func_path, 'rb'))
    # if os.path.exists(vul_candidate_func_path):
    #     vul_candidate_var = pickle.load(open(vul_candidate_var_path, 'rb'))
    vul_candidate_func, vul_candidate_var = get_vul_candidate()
    # 创建切片结果文件夹
    if os.path.exists(slice_dir_path) == 0:
        command = 'mkdir '+slice_dir_path
        os.system(command)
    bc_names = os.listdir(bc_dir_path)
    for bc_name in bc_names:
        input_path = bc_dir_path+'/'+bc_name
        if bc_name[-2:] != 'bc':
            continue
        # 创建该bc文件在切片结果文件夹下的子文件夹
        result_child_dir = slice_dir_path+'/'+bc_name[:-3]
        if os.path.exists(result_child_dir) == 0:
            command = 'mkdir '+result_child_dir
            os.system(command)
        if os.path.exists(error_command_file_path) == 0:
            command = 'touch '+error_command_file_path
            os.system(command)
        with open(error_command_file_path, 'r') as error_command_file:
            error_command = error_command_file.readlines()

        # 得到拥有函数-内部函数名信息的xml
        func_xml_path = bc_dir_path+'/'+bc_name[:-3]+'_func.xml'
        if os.path.exists(bc_dir_path+'/'+bc_name[:-3]+'.xml') == 0:
            command = "./tag/build/IRHandler "+bc_dir_path+'/'+bc_name + \
                ' --selector=getCallInfo --xml-path=' + func_xml_path
            os.system(command)
            print(command)
        func_func = tag.readCallInfoXML.getCallInfo(func_xml_path)
        # 对漏洞候选的库函数进行切片
        for func in func_func:  # 所在函数
            for func_in in func_func[func]:  # 被调用的函数
                if func_in not in vul_candidate_func[bc_name]:
                    continue
                output_path = result_child_dir+'/'+func_in+'_'+func
                # 若已存在该切片，则跳过
                if os.path.exists(output_path) > 0:
                    count += 1
                    continue
                command = dg_tools_path+'/llvm-slicer '+'-c ' + func_in + \
                    " -entry "+func + ' '+input_path+' -o '+output_path
                if command+'\n' in error_command:
                    continue
                print(command)
                os.system(command)
                if os.path.exists(output_path) == 0:
                    command2 = "echo \""+command+"\" >> "+error_command_file_path
                    os.system(command2)
                else:
                    count += 1

        # 得到拥有函数-(变量名,行号)信息的xml
        var_xml_path = bc_dir_path+'/'+bc_name[:-3]+'_var.xml'
        if os.path.exists(bc_dir_path+'/'+bc_name[:-3]+'.xml') == 0:
            command = "./tag/build/IRHandler "+bc_dir_path+'/'+bc_name + \
                ' --selector=getModuleInfo --xml-path=' + var_xml_path
            os.system(command)
            print(command)
        var_line = tag.readModuleInfoXML.getModuleInfo(var_xml_path)
        # 对漏洞候选的变量进行切片
        for func in var_line:
            for var, line in var_line[func]:
                if var not in vul_candidate_var[bc_name]:
                    continue
                if int(line) not in vul_candidate_var[bc_name][var]:
                    continue
                output_path = result_child_dir+'/'+var+'_'+line+'_'+func
                # 若已存在该切片，则跳过
                if os.path.exists(output_path) > 0:
                    count += 1
                    continue
                command = dg_tools_path+'/llvm-slicer '+'-sc ' + \
                    str(line)+':'+var + " -entry "+func + \
                    ' '+input_path+' -o '+output_path
                if command+'\n' in error_command:
                    continue
                print(command)
                os.system(command)
                if os.path.exists(output_path) == 0:
                    command2 = "echo \""+command+"\" >> "+error_command_file_path
                    os.system(command2)
                else:
                    count += 1
    print(count)


if __name__ == "__main__":
    generate_bc()
    run_dg()

# def getInfo():
#     # global count_xml
#     # 遍历每个bc文件夹，里面有bc文件
#     bc_dirs = os.listdir(unlinked_bc_dir_path)
#     for bc_dir in bc_dirs:
#         # 相对路径
#         bc_dir_path = os.path.join(
#             '%s/%s' % (unlinked_bc_dir_path, bc_dir))
#         bc_names = os.listdir(bc_dir_path)
#         # 若存在main_linux.bc，则不需要main.bc
#         if 'main_linux.bc' in bc_names and 'main.bc' in bc_names:
#             command = 'rm '+bc_dir_path+'/main.bc'
#             os.system(command)
#         for bc_name in bc_names:
#             if os.path.exists(bc_dir_path+'/'+bc_name[0:-3]+'.xml') > 0:
#                 continue
#             if bc_name[-3:] == 'xml':
#                 continue
#             command = 'env LD_LIBRARY_PATH=. '+'opt-12 -enable-new-pm=0 '+'-load ../Tag/TagLabel.so -tag-label ' + \
#                  bc_dir_path+'/'+bc_name+' -o '+bc_dir_path+'/'+bc_name[0:-3]+'-opt.bc' +\
#                 ' -selector getModuleInfo -xml-path ' + \
#                     bc_dir_path+'/'+bc_name[0:-3]+'.xml'
#             print(command)
#             os.system(command)
#             # if os.path.exists(bc_dir_path+'/'+bc_name[0:-3]+'.xml') > 0:
#             #     count_xml=count_xml+1
#             command = 'rm '+bc_dir_path+'/'+bc_name[0:-3]+'-opt.bc'
#             os.system(command)

