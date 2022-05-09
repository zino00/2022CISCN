#include "llvm/Pass.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/DebugInfo.h"
#include "llvm/IR/Value.h"
#include "llvm/IR/Instructions.h"
#include "llvm/IR/IntrinsicInst.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/ADT/PostOrderIterator.h"
#include "llvm/Support/CommandLine.h"
#include "llvm/Support/SourceMgr.h"
#include "llvm/IRReader/IRReader.h"

#include "tinyxml2/tinyxml2.h"
#include <iostream>
#include <cstdlib>
#include <fstream>
#include <sstream>
#include <map>
#include <list>
#include <unordered_set>
#include <unistd.h>

using namespace llvm;
using namespace tinyxml2;
using namespace std;

#define LOG(x...) fprintf(stderr, x)
#define FATAL(x...) do { \
    fprintf(stderr, x); \
    exit(0); \
  } while (0)

cl::opt<std::string> vuln_info_path(
    "vuln-info-path", 
    cl::desc("vuln info path"), 
    cl::value_desc("vuln-info-path"));

cl::opt<std::string> xml_path(
    "xml-path", 
    cl::desc("xml path"), 
    cl::value_desc("xml-path"));

cl::opt<std::string> arg_id(
    "id", 
    cl::desc("id"), 
    cl::value_desc("id"));

cl::opt<std::string> dbgOpt(
    "debug", 
    cl::desc("option for debug use"), 
    cl::value_desc("dbg-opt"));

cl::opt<std::string> selector(
    "selector", 
    cl::desc("argument selector"), 
    cl::value_desc("sel"),
    cl::Required);

cl::opt<std::string> inputFname(
    cl::Positional, 
    cl::desc("<InputFilePath>"), 
    cl::Required);

std::unique_ptr<Module> getLLVMIR(string fname) {
  SMDiagnostic err;
  static LLVMContext context;
  auto M = parseIRFile(fname, err, context);

  if (!M) {
    err.print(fname.c_str(), outs());
    exit(1);
  }
  return M;
}

map<string, list<size_t>> getVulnInfo(string xml_path) {
    map<string, list<size_t>> vulns_map; // path -> lines
    /*
    <container>
        <testcase>
            <file path="CWE114_Process_Control__w32_char_connect_socket_01.c">
            <flaw line="121" name="CWE-114: Process Control"/>
            </file>
        </testcase>
        ...
    */

    /* 1. 收集 XML 中所有的文件条目 */
    XMLDocument doc;

    if(doc.LoadFile(xml_path.c_str()))
        FATAL("[-] load xml file failed\n");

    XMLElement* container;
    if(doc.NoChildren())
        FATAL("[-] Cannot find <container>\n");

    container = doc.FirstChildElement("container");
    // cout << "[*] Get into container node: " << container->Name() << endl;

    for (XMLElement* testcase_elem = container->FirstChildElement("testcase"); 
        testcase_elem; testcase_elem = testcase_elem->NextSiblingElement())
    {
        // cout << "[*] Get into testcase node: " << testcase_elem->Name() << ":" << testcase_elem->GetLineNum() << endl;
        if (testcase_elem->NoChildren()) {
            LOG("[-] Cannot find <files>\n");
            continue;
        }

        for (XMLElement* file_elem = testcase_elem->FirstChildElement("file"); 
            file_elem; file_elem = file_elem->NextSiblingElement())
        {
            // cout << "[*] Get into file node: " << file_elem->Name() << ":" << file_elem->GetLineNum() << endl;
            const char* path = file_elem->Attribute("path");
            LOG("[*] Finding filename: %s\n", path);

            vulns_map[path] = list<size_t>();

            if (file_elem->NoChildren()) {
                LOG("[-] Cannot find target <flaw>\n");
                continue;
            }
            for (XMLElement* flaw_elem = file_elem->FirstChildElement("flaw"); 
                flaw_elem; flaw_elem = flaw_elem->NextSiblingElement())
            {
                const char* flaw_line_str = flaw_elem->Attribute("line");
                const char* flaw_name_str = flaw_elem->Attribute("name");
                LOG("[*] Get into flaw node: %s:%s\n", flaw_line_str, flaw_name_str);
                vulns_map[path].push_back(atoi(flaw_line_str));
            }
        }
    }
    return vulns_map;
} 

vector<size_t> getVulnInstID(map<string, list<size_t>>& vulns_map, Module& M) {
    /* 2. 遍历所有指令ID -> 对应的文件和行号 */
    vector<size_t> vuln_inst_ids;
    size_t id = 0;

    for(Function& F : M) {
        // DISubprogram* sub_prog = F.getSubprogram();
        // if(!sub_prog)
        //     continue;

        // sub_prog->getFilename();
        // if(vulns_map.find(sub_prog->))
        if (F.isDeclaration())
                continue;
        ReversePostOrderTraversal<Function *> RPOT(&F);
        for (BasicBlock* B : RPOT) {
            for (Instruction& I : *B) {
                id++;

                if(!I.hasMetadata()) 
                    continue;
                const DebugLoc& dbg_loc = I.getDebugLoc();
                DIScope *Scope = cast<DIScope>(dbg_loc.getScope());

                string&& filename = Scope->getFilename().str();
                string basename = filename;

                size_t dash_pos = filename.find_last_of('/');
                if(dash_pos != string::npos)
                    basename = filename.substr(dash_pos + 1);

                unsigned int line = dbg_loc.getLine();

                LOG("Inst(%ld): %s:%d\n", id, basename.c_str(), line);

                // 尝试在漏洞库中查询当前的文件名和行号
                auto vuln_iter = vulns_map.find(basename);
                // 如果漏洞库中存在当前文件名
                if(vuln_iter != vulns_map.end()) {
                    list<size_t>& vuln_lines = vuln_iter->second;
                    // 并且也存在当前的行号
                    if(find(vuln_lines.begin(), vuln_lines.end(), line) != vuln_lines.end()) {
                        vuln_inst_ids.push_back(id);
                    }
                }

            }
        }
    }
    return vuln_inst_ids;
}

map<string, list<pair<string, int>>> getModuleInfo(Module & M) {
    map<string, list<pair<string, int>>> info_map;
    for(Function& F : M) {
        string&& func_name = F.getName().str();
        for (BasicBlock& B : F) {
            for (Instruction& I : B) {
                CallInst* call_inst = dyn_cast<CallInst>(&I);
                if(!call_inst)
                    continue;

                Function* func = call_inst->getCalledFunction();
                if(!func || func->getName().str() != "llvm.dbg.declare")
                    continue;

                // cout << func->getName().str() << endl;
                Value* op_val = call_inst->getOperand(1);
                MetadataAsValue* meta_val = cast<MetadataAsValue>(op_val);
                Metadata* md = meta_val->getMetadata();
                DIVariable* var = dyn_cast<DIVariable>(md);

                string&& var_name = var->getName().str();
                unsigned line = var->getLine();

                LOG("%s:%d in %s\n", var_name.c_str(), line, func_name.c_str());
                
                info_map[func_name].push_back(make_pair(var_name, line));
            }
        }
    }
    return info_map;
}

map<string, unordered_set<string>> getCallInfo(Module & M) {
    map<string, unordered_set<string>> info_map;
    for(Function& F : M) {
        string&& func_name = F.getName().str();
        for (BasicBlock& B : F) {
            for (Instruction& I : B) {
                CallInst* call_inst = dyn_cast<CallInst>(&I);
                if(!call_inst)
                    continue;

                Function* func = call_inst->getCalledFunction();
                if(!func)
                    continue;

                const string && callee_name = func->getName().str();
                LOG("%s is called by %s\n", callee_name.c_str(), func_name.c_str());
                
                info_map[func_name].insert(callee_name);
            }
        }
    }
    return info_map;
}

void saveCallInfoToXml(map<string, unordered_set<string>>& info, string& path) {
    XMLDocument doc;
    XMLElement* root = doc.NewElement("root");
    doc.InsertEndChild(root);

    for(auto &func_pair : info) {
        const string& func_name = func_pair.first;
        auto callee_list = func_pair.second;

        XMLElement* function = doc.NewElement("function");
        function->SetAttribute("name", func_name.c_str());
        root->InsertEndChild(function);

        for(auto& callee_name : callee_list) {
            XMLElement* var = doc.NewElement("callee");
            var->SetAttribute("name", callee_name.c_str());
            function->InsertEndChild(var);
        }
    }
    doc.SaveFile(path.c_str());
}

void saveModuleToXml(map<string, list<pair<string, int>>>& info, string& path) {
    /*
        <root>
            <function name="g_incr">
                <variable name="c" line="3"/>
            </function>
            <function name="loop">
                <variable name="a" line="10"/>
                <variable name="b" line="10"/>
                <variable name="c" line="10"/>
                <variable name="i" line="12"/>
                <variable name="ret" line="12"/>
            </function>
        </root>
    */

    XMLDocument doc;
    XMLElement* root = doc.NewElement("root");
    doc.InsertEndChild(root);

    for(auto &func_pair : info) {
        const string& func_name = func_pair.first;
        auto pair_list = func_pair.second;

        XMLElement* function = doc.NewElement("function");
        function->SetAttribute("name", func_name.c_str());
        root->InsertEndChild(function);

        for(auto& var_pair : pair_list) {
            const string& var_name = var_pair.first;
            unsigned line = var_pair.second;

            XMLElement* var = doc.NewElement("variable");
            var->SetAttribute("name", var_name.c_str());
            var->SetAttribute("line", line);
            function->InsertEndChild(var);
        }
    }
    doc.SaveFile(path.c_str());
}

void printTargetInst(Module & M, size_t id_arg) {
    size_t id = 0;
    for(Function& F : M) {
        if (F.isDeclaration())
                continue;
        ReversePostOrderTraversal<Function *> RPOT(&F);
        for (BasicBlock* B : RPOT) {
            for (Instruction& I : *B) {
                id++;
                if(id >= id_arg) {
                    I.dump();
                    if(I.hasMetadata()) {
                        const DebugLoc& dbg_loc = I.getDebugLoc();
                        DIScope *Scope = cast<DIScope>(dbg_loc.getScope());

                        string&& filename = Scope->getFilename().str();
                        string basename = filename;

                        size_t dash_pos = filename.find_last_of('/');
                        if(dash_pos != string::npos)
                            basename = filename.substr(dash_pos + 1);

                        unsigned int line = dbg_loc.getLine();

                        printf("Inst(%ld): %s:%d\n", id, basename.c_str(), line);
                        return;
                    }
                }
            }
        }
    }
}

void testAndExit(Module& M) {
    size_t id = 0;
    if(!dbgOpt.empty()) {
        for(auto& F : M) {
            if (F.isDeclaration())
                continue;
            LOG("Func: %s\n", F.getName());
            ReversePostOrderTraversal<Function *> RPOT(&F);
            for(auto * B : RPOT) {
                for(auto& I : *B) {
                    I.dump();
                }
                LOG("End1\n");
            }
            LOG("End2\n");
        }
    }
    else {
        for(auto& F : M) {
            LOG("Func: %s\n", F.getName());
            for(auto& B : F) {
                for(auto& I : B) {
                    I.dump();
                }
                LOG("End1\n");
            }
            LOG("End2\n");
        }
    }
   
    exit(EXIT_SUCCESS);
}

int main(int argc, char **argv) {
    cl::ParseCommandLineOptions(argc, argv);
    auto M = getLLVMIR(inputFname);

    // testAndExit(*M);


    // LOG("[+] xml_path: %s\n", xml_path.c_str());
    // LOG("[+] src files: %s\n", M.getSourceFileName().c_str());
    if(selector == "getVulnInstID-saveVulnInfo") {
        ofstream ofs(vuln_info_path);
        if(!ofs)
            FATAL("Cannot open <vuln-info-path>\n");
        map<string, list<size_t>>&& vulns_map = getVulnInfo(xml_path);

        for(auto f : vulns_map) {
            ofs << f.first << " ";
            for(auto i : f.second)
                ofs << i << " ";
            ofs << endl;
        }
        LOG("Save %s VulnInfo to %s\n", xml_path.c_str(), vuln_info_path.c_str());
    }
    else if(selector == "getVulnInstID-useVulnInfo") {
        map<string, list<size_t>> vulns_map;

        ifstream ifs(vuln_info_path);
        if(!ifs)
            FATAL("Cannot open <vuln-info-path>\n");
        stringstream sst;
        string line, func_name;
        size_t size;
        list<size_t> vuln_lines;
        while(getline(ifs, line)) {
            sst.clear();
            vuln_lines.clear();
            sst << line;

            sst >> func_name;
            while(sst >> size)
                vuln_lines.push_back(size);

            vulns_map.insert(make_pair(move(func_name), move(vuln_lines)));
        }

        vector<size_t>&& vuln_ids = getVulnInstID(vulns_map, *M);

        for(auto id : vuln_ids)
            cout << id << "\t";
    } else if (selector == "getModuleInfo") {
        auto&& module_info_map = getModuleInfo(*M);
        saveModuleToXml(module_info_map, xml_path);
    } else if (selector == "printTargetInst") {
        printTargetInst(*M, atoi(arg_id.c_str()));
    } else if (selector == "getCallInfo") {
        auto&& module_info_map = getCallInfo(*M);
        saveCallInfoToXml(module_info_map, xml_path);
    }
    else 
        FATAL("Cannot recognize selector(\"%s\")", selector.c_str());

    return 0;
}