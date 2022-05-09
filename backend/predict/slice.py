import os
import json
import pickle
from tag.readModuleInfoXML import getModuleInfo
from tag.readCallInfoXML import getCallInfo
from predict.get_vul_linenumber import c2res, get_all_function_list
import path_required
import multiprocessing


# llvm的安装路径
llvm_build = path_required.llvm_build
# txt 文件路径 包含敏感函数名
sensitive_funcname_txt_path = path_required.sensitive_funcname_txt_path
# tag工具文件夹的路径
tag_path = path_required.tag_path
# dg工具的路径
dg_tools_path = path_required.dg_tools_path
# key:连接后的bc名, value:由被连接bc对应c文件名构成的列表 --由link生成
bc_c_dict = {}


def link(single_dir_path):
    '''
    连接,在get_vul_candidate()中调用
    '''
    # 连接后bc文件目录的路径
    bc_dir_path = single_dir_path+'/bcfile'
    # 未连接bc文件目录的路径
    unlinked_bc_dir_path = single_dir_path+'/unlinked_bcfile'
    # ir与c文件对应关系字典的路径
    bc_c_dict_path = single_dir_path+'/bc_c_dict.pkl'
    global bc_c_dict
    # 创建连接后的bc所在文件夹
    if os.path.exists(bc_dir_path) == 0:
        command = 'mkdir '+bc_dir_path
        os.system(command)
    unlinked_bc_child_dir_paths=[]
    unlinked_bc_child_dir_paths.append(unlinked_bc_child_dir_path)
    for current_filepath, unlinked_bc_child_dirnames, filenames in os.walk(unlinked_bc_dir_path):
        unlinked_bc_child_dir_paths.append(current_filepath+unlinked_bc_child_dirnames)
    for unlinked_bc_child_dir_path in unlinked_bc_child_dir_paths:
        unlinked_bc_names = os.listdir(unlinked_bc_child_dir_path)
        # 若目录下不是bc文件,是目录,则跳过
        if len(unlinked_bc_names) > 0 and os.path.isdir(unlinked_bc_child_dir_path+'/'+unlinked_bc_names[0]):
            continue
        # 未连接的bc相对于所有bc文件所在目录的路径
        unlinked_bc_relative_path = unlinked_bc_child_dir_path[unlinked_bc_child_dir_path.find(
            unlinked_bc_dir_path)+len(unlinked_bc_dir_path):]
        current_unlinked_bc_path=unlinked_bc_child_dir_path
        for dirname in unlinked_bc_relative_path.split('/')[:-1]:
            current_unlinked_bc_path+=dirname
            if os.path.exists(current_unlinked_bc_path) == 0:
                os.mkdir(current_unlinked_bc_path)
        # 连接后的bc名（一个文件不连接）
        bc_name = ''
        if len(unlinked_bc_names) > 1:
            bc_name = unlinked_bc_relative_path[unlinked_bc_relative_path.find(current_unlinked_bc_path)+len(unlinked_bc_dir_path):]+'.bc'
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
            os.system(command)
        elif len(unlinked_bc_names) == 1:
            command = "mv "+unlinked_bc_child_dir_path + \
                '/' + bc_name+" " + bc_dir_path+'/'+bc_name
            os.system(command)
    with open(bc_c_dict_path, 'wb') as file:
        pickle.dump(bc_c_dict, file)


def get_single_bc_vul_candicate(bc_name, function_list, mutex, single_dir_path):
    # print("begin")
    # 漏洞字典的路径
    vul_candidate_func_path = single_dir_path+'/vul_candidate_func.pkl'
    vul_candidate_var_path = single_dir_path+'/vul_candidate_var.pkl'
    vul_json_file_paths = []
    for c_path in bc_c_dict[bc_name]:
        vul_json_file_paths.append(c2res(c_path, function_list))
    # 对含漏洞候选的pkl文件上锁
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
    mutex.release()
    # print("finish")


def get_vul_candidate(single_dir_path):
    '''
    得到每个bc文件的漏洞候选,在run_dg()中被调用
    '''
    # 连接后bc文件目录的路径
    bc_dir_path = single_dir_path+'/bcfile'
    vul_candidate_func_path = single_dir_path+'/vul_candidate_func.pkl'
    vul_candidate_var_path = single_dir_path+'/vul_candidate_var.pkl'
    # 切片所在目录
    slice_dir_path = single_dir_path+'/slice_file'
    # 得到bc文件-c文件的映射
    link(single_dir_path)
    # 得到敏感函数列表 function_list
    function_list = get_all_function_list(sensitive_funcname_txt_path)
    # 遍历bc文件夹中的bc文件
    bc_names = os.listdir(bc_dir_path)
    # (bc_name,function,linenumber{})的映射
    vul_candidate_func = {}
    # (bc_name,variable,linenumber{})的映射
    vul_candidate_var = {}
    # with open(vul_candidate_func_path, 'wb') as file:
    #     pickle.dump(vul_candidate_func, file)
    # with open(vul_candidate_var_path, 'wb') as file:
    #     pickle.dump(vul_candidate_var, file)
    # 加载已保存的漏洞候选映射
    if os.path.exists(vul_candidate_func_path):
        vul_candidate_func = pickle.load(open(vul_candidate_func_path, 'rb'))
    if os.path.exists(vul_candidate_var_path):
        vul_candidate_var = pickle.load(open(vul_candidate_var_path, 'rb'))
    # 遍历bc文件,得到漏洞候选（线程池）
    p2 = multiprocessing.Pool(8)
    async_results = []
    mutex = multiprocessing.Manager().Lock()
    for bc_name in bc_names:
        # 不是bc文件，则跳过
        if bc_name[-2:] != 'bc':
            continue
        # 若bc文件已处理，则跳过
        if bc_name in vul_candidate_func.keys() and bc_name in vul_candidate_var.keys():
            continue
        async_results.append(p2.apply_async(get_single_bc_vul_candicate, args=(
            bc_name, function_list, mutex, single_dir_path)))
    p2.close()
    p2.join()
    vul_candidate_func = pickle.load(open(vul_candidate_func_path, 'rb'))
    vul_candidate_var = pickle.load(open(vul_candidate_var_path, 'rb'))
    return vul_candidate_func, vul_candidate_var


def run_dg(single_dir_path):
    # 获取漏洞字典
    vul_candidate_func, vul_candidate_var = get_vul_candidate(single_dir_path)
    # 切片所在目录
    slice_dir_path = single_dir_path+'/slice_file'
    # 连接后bc文件目录的路径
    bc_dir_path = single_dir_path+'/bcfile'
    # 错误dg命令的路径
    error_command_file_path = single_dir_path+'/error.txt'
    # 创建切片结果文件夹
    if os.path.exists(slice_dir_path) == 0:
        os.mkdir(slice_dir_path)
    bc_names = os.listdir(bc_dir_path)
    for bc_name in bc_names:
        input_path = bc_dir_path+'/'+bc_name
        if bc_name[-2:] != 'bc':
            continue
        # 创建该bc文件在切片结果文件夹下的子文件夹
        result_child_dir = slice_dir_path+'/'+bc_name[:-3]
        if os.path.exists(result_child_dir) == 0:
            os.mkdir(result_child_dir)
        if os.path.exists(error_command_file_path) == 0:
            command = 'touch '+error_command_file_path
            os.system(command)
        with open(error_command_file_path, 'r') as error_command_file:
            error_command = error_command_file.readlines()
        # 得到拥有函数-内部函数名信息的xml
        func_xml_path = bc_dir_path+'/'+bc_name[:-3]+'_func.xml'
        if os.path.exists(bc_dir_path+'/'+bc_name[:-3]+'.xml') == 0:
            command = tag_path+"/build/IRHandler "+bc_dir_path+'/'+bc_name + \
                ' --selector=getCallInfo --xml-path=' + func_xml_path
            os.system(command)
        func_func = getCallInfo(func_xml_path)
        # 对漏洞候选的库函数进行切片
        for func in func_func:  # 所在函数
            for func_in in func_func[func]:  # 被调用的函数
                if func_in not in vul_candidate_func[bc_name]:
                    continue
                output_path = result_child_dir+'/'+func_in+'_'+func
                # 若已存在该切片，则跳过
                if os.path.exists(output_path) > 0:
                    continue
                command = dg_tools_path+'/llvm-slicer '+'-c ' + func_in + \
                    " -entry "+func + ' '+input_path+' -o '+output_path
                if command+'\n' in error_command:
                    continue
                os.system(command)
                if os.path.exists(output_path) == 0:
                    command2 = "echo \""+command+"\" >> "+error_command_file_path
                    os.system(command2)
        # 得到拥有函数-(变量名,行号)信息的xml
        var_xml_path = bc_dir_path+'/'+bc_name[:-3]+'_var.xml'
        if os.path.exists(bc_dir_path+'/'+bc_name[:-3]+'.xml') == 0:
            command = tag_path+"/build/IRHandler "+bc_dir_path+'/'+bc_name + \
                ' --selector=getModuleInfo --xml-path=' + var_xml_path
            os.system(command)
        var_line = getModuleInfo(var_xml_path)
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
                    continue
                command = dg_tools_path+'/llvm-slicer '+'-sc ' + \
                    str(line)+':'+var + " -entry "+func + \
                    ' '+input_path+' -o '+output_path
                if command+'\n' in error_command:
                    continue
                os.system(command)
                if os.path.exists(output_path) == 0:
                    command2 = "echo \""+command+"\" >> "+error_command_file_path
                    os.system(command2)
