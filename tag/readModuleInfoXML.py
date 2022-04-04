#! python3
from xml.dom import minidom

def getModuleInfo(filepath):
    '''
    brief: 读取 ll 所生成的变量与函数信息
    return: 一个存放 (function, [(var_name, line), ...]) 映射的集合
    例如：{'g_incr': [('c', '3')], 'loop': [('a', '10'), ('b', '10'), ('c', '10'), ('i', '12'), ('ret', '12')]}
    '''
    module_info_dict = {}
    # 注：执行 minidom.parse 时会卡住 5s 左右，可能是库函数内部实现问题
    dom = minidom.parse(filepath)
    root = dom.documentElement
    for function in root.getElementsByTagName('function'):
        func_name = function.getAttribute('name')
        module_info_dict[func_name] = []
        for variable in function.getElementsByTagName('variable'):
            var_name = variable.getAttribute('name')
            line = variable.getAttribute('line')
            module_info_dict[func_name].append((var_name, line))
    return module_info_dict


if __name__ == "__main__":
    filepath = "/tmp/output.xml"
    module_info = getModuleInfo(filepath)
    print(module_info)