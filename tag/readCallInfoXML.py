#! python3
from xml.dom import minidom

def getCallInfo(filepath):
    module_info_dict = {}
    # 注：执行 minidom.parse 时会卡住 5s 左右，可能是库函数内部实现问题
    dom = minidom.parse(filepath)
    root = dom.documentElement
    for function in root.getElementsByTagName('function'):
        func_name = function.getAttribute('name')
        module_info_dict[func_name] = []
        for callee in function.getElementsByTagName('callee'):
            callee_name = callee.getAttribute('name')
            module_info_dict[func_name].append(callee_name)
    return module_info_dict


if __name__ == "__main__":
    filepath = "/tmp/output.xml"
    module_info = getCallInfo(filepath)
    print(module_info)