import os
import path_required

# llvm的安装路径
llvm_build = path_required.llvm_build


def generate_bc(single_dir_path):
    # c文件目录路径
    src_dir_path = single_dir_path+'/C_file'
    # c文件编译依赖的目录路径，不存在则为''
    support_dir_path = path_required.support_dir_path
    # 未连接bc文件目录的路径
    unlinked_bc_dir_path = single_dir_path+'/unlinked_bcfile'
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
            # 若编译失败，则删除所有文件并返回0
            if os.path.exists(unlinked_bc_child_dir_path + '/' + file_name + '.bc') == 0:
                command = 'rm -rf '+unlinked_bc_dir_path
                os.system(command)
                command = 'rm -rf '+src_dir_path
                os.system(command)
                return 0
    # 全部文件编译成功，则返回1
    return 1
