#include "llvm-13/llvm/Pass.h"
#include "llvm-13/llvm/IR/Module.h"
#include "llvm-13/llvm/Support/raw_ostream.h"

#include "tinyxml2/tinyxml2.h"
#include "llvm/Support/CommandLine.h"

using namespace llvm;

static cl::opt<std::string> xml_path("xml-path", cl::desc("xml path used in Tag-Label Pass"), cl::value_desc("xml-path"));

namespace {

class TagLabel final : public ModulePass
{
public:
	static char ID;

	TagLabel() : ModulePass(ID) {}
	virtual ~TagLabel() override {}

  	// We don't modify the program, so we preserve all analysis.
	virtual void getAnalysisUsage(AnalysisUsage & AU) const override
	{
		AU.setPreservesAll();
	}

	virtual bool runOnModule(Module & M) override
	{
        printf("xml_path: %s\n", xml_path.c_str());
		printf("src files: %s\n", M.getSourceFileName().c_str());
		
		return false;
	}
};

char TagLabel::ID = 0;
RegisterPass < TagLabel > X (
	"tag-label",
	"tag vuln label to slices");

}  // namespace anonymous