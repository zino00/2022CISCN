# clang-12 -O0 -Xclang -disable-O0-optnone -g -emit-llvm -c tests/test.c -o tests/test.bc
# env LD_LIBRARY_PATH=. \
#         opt-12 -enable-new-pm=0 \
#         -load TagLabel.so -tag-label \
#         tests/test.bc -o tests/test-opt.bc \
#         -selector getModuleInfo -xml-path /tmp/output.xml
import os
import readModuleInfoXML
src_folder = "testcases"
llvm_build = '/usr/local/llvm'
support_folder = "testcasesupport"
all_bc_folder = 'bcfiles'
result_folder = 'sliced_unlinked'
current_folder_path = '/home/yuhan/桌面/Juliet_Test_Suite_v1.3_for_C_Cpp/C/'
dg_tools_path = '/home/yuhan/dg/tools/'
count_c=0
count_bc=0
count_xml=0
count_bc_sliced=0
count_ll=0
# dir_name:当前所在文件夹，folder_path:文件夹相对路径，result_folder_name：结果所在的文件夹名
def generate_bc(dir_name, folder_path, result_folder_name):
    global count_c
    global count_bc
    if os.path.exists(all_bc_folder) == 0:
        command = 'mkdir '+all_bc_folder
        os.system(command)
    if folder_path != '':
        folder_path = folder_path+'/'
    folder_path = folder_path+dir_name
    if result_folder_name != '':
        result_folder_name = result_folder_name+'_'
    if dir_name != src_folder:
        result_folder_name = result_folder_name+dir_name
    dirs = os.listdir(folder_path)
    success=1
    for dir in dirs:
        # 判断是否是子目录,若是，则进入目录
        if os.path.isdir(folder_path+'/'+dir) == True:
            generate_bc(dir, folder_path, result_folder_name)
        # 对于c文件，进行切片
        else:
            src_file = dir
            if os.path.exists(all_bc_folder+'/'+result_folder_name) == 0:
                command = "mkdir "+all_bc_folder+'/'+result_folder_name
                os.system(command)
            if src_file[-2:] == '.c' and src_file[:2] != 'io':
                count_c=count_c+1
                file_name = src_file[:src_file.find('.')]
                if os.path.exists(all_bc_folder + '/' + result_folder_name + '/' + file_name + '.bc') > 0:
                    count_bc=count_bc+1
                    continue
                command = llvm_build+'/bin/clang -c -g -I '+support_folder+' -emit-llvm -Xclang -disable-O0-optnone ' + \
                    folder_path+'/'+src_file+' -o ' + all_bc_folder + \
                    '/' + result_folder_name + '/' + file_name + '.bc'
                os.system(command)
                if os.path.exists(all_bc_folder+'/'+result_folder_name + '/' + file_name + '.bc') >0:
                    count_bc=count_bc+1
    #           else
    #                 success=0
    #                 break
    #若编译失败，则删除该c文件对应结果子文件夹的所有文件
    # if success==0:
    #     command='rm -rf '+all_bc_folder+'/'+result_folder_name
    #     os.system(command)       

def getInfo():
    global count_xml
    # 遍历每个bc文件夹，里面有bc文件
    bc_folders = os.listdir(all_bc_folder)
    for bc_folder in bc_folders:
        # 相对路径
        bc_folder_path = os.path.join('%s/%s' % (all_bc_folder, bc_folder))
        bc_names = os.listdir(bc_folder_path)
        # 若存在main_linux.bc，则不需要main.bc
        if 'main_linux.bc' in bc_names and 'main.bc' in bc_names:
            command = 'rm '+bc_folder_path+'/main.bc'
            os.system(command)
        for bc_name in bc_names:
            if os.path.exists(bc_folder_path+'/'+bc_name[0:-3]+'.xml') > 0:
                continue
            if bc_name[-3:]=='xml':
                continue
            command = 'env LD_LIBRARY_PATH=. '+'opt-12 -enable-new-pm=0 '+'-load ../Tag/TagLabel.so -tag-label ' + \
                 bc_folder_path+'/'+bc_name+' -o '+bc_folder_path+'/'+bc_name[0:-3]+'-opt.bc'+\
                ' -selector getModuleInfo -xml-path '+bc_folder_path+'/'+bc_name[0:-3]+'.xml'
            print(command)
            os.system(command)
            if os.path.exists(bc_folder_path+'/'+bc_name[0:-3]+'.xml') > 0:
                count_xml=count_xml+1
            command='rm '+bc_folder_path+'/'+bc_name[0:-3]+'-opt.bc'
            os.system(command)

def run_dg():
    global count_bc_sliced
    global count_ll
    if os.path.exists(result_folder) == 0:
        command = 'mkdir '+result_folder
        os.system(command)
    # 遍历每个bc文件夹，里面有bc文件
    bc_folders = os.listdir(all_bc_folder)
    for bc_folder in bc_folders:
        # 相对路径
        bc_folder_path = os.path.join('%s/%s' % (all_bc_folder, bc_folder))
        bc_names = os.listdir(bc_folder_path)
        #遍历bc文件
        for bc_name in bc_names:
            #所有切片都成功的标志
            flag=1
            if bc_name[-3:]=='xml':
                continue
            input_path = current_folder_path+bc_folder_path+'/'+bc_name
            # 创建该bc文件在结果文件夹下的子文件夹
            result_child_folder = os.path.join('%s/%s' % (result_folder, bc_name[:-3]))
            if os.path.exists(result_child_folder) == 0:
                command = 'mkdir '+result_child_folder
                os.system(command)
            xml_path=bc_folder_path+'/'+bc_name[0:-3]+'.xml'
            info=readModuleInfoXML.getModuleInfo(xml_path)
            for func in info.keys():
                for i in range(len(info[func])):
                    var,line=info[func][i]
                    output_path = current_folder_path+result_child_folder+'/'+var+'_'+line+'.ll'
                    if os.path.exists(output_path) > 0:
                        count_ll=count_ll+1
                        continue
                    command = dg_tools_path+'llvm-slicer'+' -sc ' + \
                    str(line)+':'+var+' -entry '+func+' '+input_path+' -o '+output_path
                    print(command)
                    os.system(command)
                    command = 'llvm-dis ' + output_path
                    os.system(command)
                    #切片失败则删除该bc文件对应的结果文件夹
                    if os.path.exists(output_path) == 0:
                        flag=0
                        command='rm -rf '+current_folder_path+result_child_folder
                        os.system(command)
                        break
                    count_ll=count_ll+1
                if flag==0:
                    break
            if flag==0:
                break
            count_bc_sliced=count_bc_sliced+1

# def my_delete():
#     ll_folders=os.listdir(result_folder)
#     for ll_folder in ll_folders:
#         ll_names=os.listdir(result_folder+'/'+ll_folder)
#         if len(ll_names) ==0:
#             command='rm -rf '+result_folder+'/'+ll_folder
#             os.system(command)
#         for ll_name in ll_names:
#             if  ll_name[-6:]=='.ll.ll':
#                 command='mv '+result_folder+'/'+ll_folder+'/'+ll_name+' '+result_folder+'/'+ll_folder+'/'+ll_name[:-3]
#                 print(command)
#                 os.system(command)
                    

if __name__ == "__main__":
    #generate_bc(src_folder, '', '')
    getInfo()
    run_dg()
    print("成功对"+str(count_bc_sliced)+"个文件进行切片，得到"+str(count_ll)+"个切片"+'\n')
    print('\n')
    print('c文件共'+str(count_c)+"个，其中"+str(count_bc)+"个成功转为ir")
    # my_delete()
