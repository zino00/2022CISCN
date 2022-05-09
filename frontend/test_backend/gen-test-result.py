# encoding: utf-8
from xml.dom import minidom
import json

src_path = "test/"
cppsrc_paths = [
    "CWE665_Improper_Initialization__char_cat_61b.c",
    "CWE122_Heap_Based_Buffer_Overflow__c_CWE193_wchar_t_cpy_81_bad.cpp",
    "CWE127_Buffer_Underread__char_declare_memcpy_81_bad.cpp",
]

def readManifestXML(filepath):
    xmldict = {}

    dom = minidom.parse(filepath)
    root = dom.documentElement
    for testcase in root.getElementsByTagName('testcase'):
        for file in testcase.getElementsByTagName('file'):
            filename = file.getAttribute('path')
            xmldict[filename] = []
            for flaw in file.getElementsByTagName('flaw'):
                linestr = flaw.getAttribute('line')
                xmldict[filename].append(int(linestr))
            if len(xmldict[filename]) == 0:
                xmldict.pop(filename)

    return xmldict


def readSrc(filepath):
    with open(filepath, "r") as f:
        src = f.read()
    return src


if __name__ == "__main__":
    res = {"result":[]}

    xmldict = readManifestXML(src_path + "manifest.xml")
    # print(xmldict)

    for fn in cppsrc_paths:
        src = readSrc(src_path + fn)
        # print(src)
        # print(xmldict[fn])
        res["result"].append({
            "filepath": fn,
            "code": src,
            "vuln": xmldict[fn]
        })

    with open("test-result.json", "w") as f:
        json.dump(res, f)
