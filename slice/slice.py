import os
import json
import tag.readModuleInfoXML
import get_vul_linenumber
# c文件目录路径
src_dir_path = get_vul_linenumber.C_source_dir
# txt 文件路径 包含敏感函数名
sensitive_funcname_txt_path = "/home/yuhan/桌面/2022CISCN/slice/sensitive_funcname.txt"
# c文件编译依赖的目录路径
support_dir_path = "/home/yuhan/桌面/Juliet/C/testcasesupport"
# llvm的安装路径
llvm_build = '/usr/lib/llvm-12'

# 当前文件夹的路径
current_dir_path = '/home/yuhan/桌面/Juliet_Test_Suite_v1.3_for_C_Cpp/C'
# dg工具的路径
dg_tools_path = '/home/yuhan/dg/tools'

# 未连接bc文件目录的路径
unlinked_bc_dir_path = '/home/yuhan/桌面/Juliet/C/unlinked_bcfile'
# 连接后bc文件目录的路径
bc_dir_path = '/home/yuhan/桌面/Juliet/C/bcfile'
# 切片结果目录的路径
result_dir = '/home/yuhan/桌面/Juliet/C/slice_file'


# dir_name:当前所在文件夹，dir_path:被遍历目录的路径，result_dir_name：结果所在的目录名
def generate_bc(dir_name, dir_path, result_dir_name):
    # 若不存在bc文件保存的路径,则创建
    if os.path.exists(unlinked_bc_dir_path) == 0:
        command = 'mkdir '+unlinked_bc_dir_path
        os.system(command)
    if dir_path != '':
        dir_path = dir_path+'/'
    dir_path = dir_path+dir_name
    # 结果子目录名
    if result_dir_name != '':
        result_dir_name = result_dir_name+'_'
    if dir_name != src_dir_path:
        result_dir_name = result_dir_name+dir_name
    dirs = os.listdir(dir_path)
    success = 1
    for dir in dirs:
        # 判断是否是子目录,若是，则进入目录
        if os.path.isdir(dir_path+'/'+dir) == True:
            generate_bc(dir, dir_path, result_dir_name)
        # 对于c文件，进行转化
        else:
            # # 结果子目录名与c文件的相同
            # result_dir_name = dir_name
            src_filename = dir
            if os.path.exists(unlinked_bc_dir_path+'/'+result_dir_name) == 0:
                command = "mkdir "+unlinked_bc_dir_path+'/'+result_dir_name
                os.system(command)
            if src_filename[-2:] == '.c' or src_filename == 'main.cpp' or src_filename == 'main_linux.cpp':
                file_name = src_filename[:src_filename.find('.')]
                # 若该文件bc已生成,则遍历下一个
                if os.path.exists(unlinked_bc_dir_path + '/' + result_dir_name + '/' + file_name + '.bc') > 0:
                    continue
                # 编译命令
                command = llvm_build+'/bin/clang -c -g  -I '+support_dir_path+' -emit-llvm -Xclang -disable-O0-optnone ' + \
                    dir_path+'/'+src_filename+' -o ' + unlinked_bc_dir_path + \
                    '/' + result_dir_name + '/' + file_name + '.bc'
                # print(command)
                os.system(command)
                if os.path.exists(unlinked_bc_dir_path+'/'+result_dir_name + '/' + file_name + '.bc') == 0:
                    success = 0
                    break
    # 若编译失败，则删除该c文件所在文件夹和对应结果子文件夹的所有文件
    if success == 0:
        command = 'rm -rf '+dir_path
        print(command)
        os.system(command)
        command = 'rm -rf '+unlinked_bc_dir_path+'/'+result_dir_name
        os.system(command)


def link():
    '''
    连接,在get_vul_candidate()中调用
    '''
    # 创建连接后的bc所在文件夹
    if os.path.exists(bc_dir_path) == 0:
        command = 'mkdir '+bc_dir_path
        os.system(command)
    bc_c_dict = {}  # key:连接后的bc名, value:由被连接bc对应c文件名构成的列表
    unlinked_bc_dirs = os.listdir(unlinked_bc_dir_path)
    for unlinked_bc_dir in unlinked_bc_dirs:
        unlinked_bc_child_dir_path = unlinked_bc_dir_path+'/'+unlinked_bc_dir
        unlinked_bc_names = os.listdir(unlinked_bc_child_dir_path)
        command = llvm_build+"/bin/llvm-link "
        bc_c_dict[unlinked_bc_dir+".bc"] = []
        # 若有main_linux.bc存在,则不需要连接main.bc
        main_linux_exist = 0
        for unlinked_bc_name in unlinked_bc_names:
            if unlinked_bc_name == "main_linux.bc":
                main_linux_exist = 1
                break
        for unlinked_bc_name in unlinked_bc_names:
            if main_linux_exist == 1 and unlinked_bc_name == "main.bc":
                continue
            if unlinked_bc_name[0:4] == "main":
                c_name = unlinked_bc_name[:-3]+".cpp"
            else:
                c_name = unlinked_bc_name[:-3]+".c"
            bc_c_dict[unlinked_bc_dir+".bc"].append(c_name)
            command = command+unlinked_bc_child_dir_path+'/'+unlinked_bc_name+" "
        command = command+"-o "+bc_dir_path+'/'+unlinked_bc_dir+".bc"
        os.system(command)
    return bc_c_dict


def get_vul_candidate():
    '''
    得到每个bc文件的漏洞候选,在run_dg()中被调用
    '''
    # 得到字典key:bc文件名,value:对应c文件名
    bc_c_dict = link()
    # 得到敏感函数列表 function_list
    function_list = get_vul_linenumber.get_all_function_list(
        sensitive_funcname_txt_path)
    # 遍历bc文件夹中的bc文件
    bc_names = os.listdir(bc_dir_path)
    #(bc_name,function,linenumber{})的映射
    vul_candidate_func = {}
    #(bc_name,variable,linenumber{})的映射
    vul_candidate_var = {}
    # 遍历bc文件,得到漏洞候选
    for bc_name in bc_names:
        if bc_name[-3:] == 'xml':
            continue       
        # 所有切片都成功的标志
        flag = 1
        vul_candidate_func[bc_name] = {}
        vul_candidate_var[bc_name] = {}
        # 遍历该bc文件对应的c文件
        for c_name in bc_c_dict[bc_name]:
            name_line_json_file = open(
                get_vul_linenumber.c2res(bc_name[:-3]+'/'+c_name, function_list))
            print(name_line_json_file)
            name_line_json = json.load(name_line_json_file)
            # 遍历漏洞候选的定位
            for name_line in name_line_json:
                line=name_line['lineNumber']
                if 'function' in name_line:
                    func = name_line['function']
                    if  func not in vul_candidate_func[bc_name]:
                        vul_candidate_func[bc_name][func]=[]
                    vul_candidate_func[bc_name][func].append(line) 
                elif 'variable' in name_line or 'assignment' in name_line:
                    if 'variable' in name_line:
                        var = name_line['variable']
                    else:
                        var = name_line['assignment']
                    if  var not in vul_candidate_var[bc_name]:
                        vul_candidate_var[bc_name][var]=[]
                    vul_candidate_var[bc_name][var].append(line) 
    return vul_candidate_func, vul_candidate_var


def run_dg():
    # 得到漏洞候选字典
    vul_candidate_func, vul_candidate_var = get_vul_candidate()
    # 创建切片结果文件夹
    if os.path.exists(result_dir) == 0:
        command = 'mkdir '+result_dir
        os.system(command)
    bc_names = os.listdir(bc_dir_path)
    for bc_name in bc_names:
        input_path = bc_dir_path+'/'+bc_name
        if bc_name[-3:] == 'xml':
            continue
        # 创建该bc文件在切片结果文件夹下的子文件夹
        result_child_dir = result_dir+'/'+bc_name[:-3]
        if os.path.exists(result_child_dir) == 0:
            command = 'mkdir '+result_child_dir
            os.system(command)
        # 对漏洞候选的库函数进行切片
        for func in vul_candidate_func[bc_name]:
            output_path = result_child_dir+'/'+func
            if os.path.exists(output_path) > 0:
                continue
            command = dg_tools_path+'/llvm-slicer '+'-c ' + \
                func + ' '+input_path+' -o '+output_path
            print(command)
            os.system(command)
            command = 'llvm-dis ' + output_path
            print(command)
            os.system(command)
        # 得到拥有函数-变量名-行号信息的xml
        if os.path.exists(bc_dir_path+'/'+bc_name[:-3]+'.xml') == 0:
            command = "./tag/build/IRHandler "+bc_dir_path+'/'+bc_name + \
                ' --selector=getModuleInfo --xml-path=' + \
                bc_dir_path+'/'+bc_name[:-3]+'.xml'
            os.system(command)
            print(command)
        var_line = tag.readModuleInfoXML.getModuleInfo(bc_dir_path+'/'+bc_name[:-3]+'.xml')
        # 对漏洞候选的变量进行切片
        for func in var_line:
            for var, line in var_line[func]:
                if var not in vul_candidate_var[bc_name]:
                    continue
                if int(line) not in vul_candidate_var[bc_name][var]:
                    continue
                output_path = result_child_dir+'/'+var+'_'+line+'_'+func
                if os.path.exists(output_path) > 0:
                    continue
                command = dg_tools_path+'/llvm-slicer '+'-sc ' + \
                    str(line)+':'+var + " -entry "+func + \
                    ' '+input_path+' -o '+output_path
                print(command)
                os.system(command)
                # command = 'llvm-dis ' + output_path
                # print(command)
                # os.system(command)                
            # #切片失败则删除该bc文件对应的结果文件夹
            #     if os.path.exists(output_path) == 0:
            #         flag = 0
            #         command = 'rm -rf '+result_child_dir
            #         os.system(command)
            #         break
        # if flag == 0:
        #     break


if __name__ == "__main__":
    generate_bc(src_dir_path, '', '')
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