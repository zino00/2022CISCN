#include "llvm/Pass.h"
#include "llvm/IR/Module.h"
#include "llvm/IR/DebugInfo.h"
#include "llvm/IR/Value.h"
#include "llvm/Support/raw_ostream.h"
#include "llvm/Support/CommandLine.h"

#include "tinyxml2/tinyxml2.h"
#include <iostream>
#include <cstdlib>
#include <map>
#include <list>
#include <unistd.h>

using namespace llvm;
using namespace tinyxml2;
using namespace std;

#define LOG(x...) fprintf(stderr, x)
#define FATAL(x...) do { \
    fprintf(stderr, x); \
    exit(0); \
  } while (0)

static cl::opt<std::string> xml_path("xml-path", cl::desc("xml path used in Tag-Label Pass"), cl::value_desc("xml-path"));

namespace {

class TagLabel final : public ModulePass
{
public:
	static char ID;
    
    XMLDocument doc;
    map<string, list<size_t>> vulns_map; // path -> lines

	TagLabel() : ModulePass(ID) {}
	virtual ~TagLabel() override {}

  	// We don't modify the program, so we preserve all analysis.
	virtual void getAnalysisUsage(AnalysisUsage & AU) const override
	{
		AU.setPreservesAll();
	}

    void get_vuln_info() {
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
                for (XMLElement* flaw_elem = file_elem->FirstChildElement(); 
                    flaw_elem; flaw_elem = flaw_elem->NextSiblingElement())
                {
                    const char* flaw_line_str = flaw_elem->Attribute("line");
                    const char* flaw_name_str = flaw_elem->Attribute("name");
                    LOG("[*] Get into flaw node: %s:%s\n", flaw_line_str, flaw_name_str);
                    vulns_map[path].push_back(atoi(flaw_line_str));
                }
            }
        }
    } 

    vector<size_t> get_vuln_inst_id(Module& M) {
        /* 2. 遍历所有指令ID -> 对应的文件和行号 */
        vector<size_t> vuln_inst_ids;
        size_t id = 0;

        for(Function& F : M) {
            // DISubprogram* sub_prog = F.getSubprogram();
            // if(!sub_prog)
            //     continue;

            // sub_prog->getFilename();
            // if(vulns_map.find(sub_prog->))
            for (BasicBlock& B : F) {
                for (Instruction& I : B) {
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

	virtual bool runOnModule(Module & M) override
	{
        LOG("[+] xml_path: %s\n", xml_path.c_str());
        LOG("[+] src files: %s\n", M.getSourceFileName().c_str());

        get_vuln_info();
        vector<size_t> vuln_ids = get_vuln_inst_id(M);

        for(auto id : vuln_ids)
            cout << id << "\t";

		return false;
	}
};

char TagLabel::ID = 0;
RegisterPass < TagLabel > X (
	"tag-label",
	"tag vuln label to slices");

}  // namespace anonymous