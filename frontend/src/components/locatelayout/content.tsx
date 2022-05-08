import { defineComponent } from 'vue'
import { Layout } from 'ant-design-vue'
import CodeMirror from "codemirror-editor-vue3";
import "codemirror/mode/clike/clike.js"
import "codemirror/theme/yonce.css"

let WRAP_CLASS = "CodeMirror-activeline";
let BACK_CLASS = "CodeMirror-activeline-background";
let GUTT_CLASS = "CodeMirror-activeline-gutter";

const LocateContent = defineComponent({
    name: 'LocateContent',
    setup() {
        var code = ``;
        var vulns = [];
        return { code, vulns }
    },
    methods: {
        update(code, vulns) {
            let cm = this.$refs.Locate_Code_Mirror.cminstance;
            // 修改代码
            cm.setValue(code);
            // 重置先前的高亮
            for (var i = 0; i < this.vulns.length; i++) {
                cm.removeLineClass(this.vulns[i] - 1, "wrap", WRAP_CLASS);
                cm.removeLineClass(this.vulns[i] - 1, "background", BACK_CLASS);
                cm.removeLineClass(this.vulns[i] - 1, "gutter", GUTT_CLASS);
            }
            // 更新现有的高亮
            this.vulns = vulns;
            for (var i = 0; i < this.vulns.length; i++) {
                // console.log(this.vulns[i] - 1)
                cm.addLineClass(this.vulns[i] - 1, "wrap", WRAP_CLASS);
                cm.addLineClass(this.vulns[i] - 1, "background", BACK_CLASS);
                cm.addLineClass(this.vulns[i] - 1, "gutter", GUTT_CLASS);
            }
            // 设置curso
            if(this.vulns && this.vulns.length > 0)
                cm.setCursor(this.vulns[0] - 1)
        }
    },
    render() {
        const cmOptions = {
            mode: "text/x-c++src", // 语言模式
            theme: "yonce", // 主题
            lineNumbers: true, // 显示行号
            smartIndent: true, // 智能缩进
            indentUnit: 2, // 智能缩进单位为4个空格长度
            foldGutter: true, // 启用行槽中的代码折叠
            styleActiveLine: true, // 显示选中行的样式
          };
        const codeMirrorOnChange = (val, cm) => {
            // console.log(val);
            // console.log(val);
            
        };
        return (
            <CodeMirror ref="Locate_Code_Mirror" options={cmOptions} border value={this.code} onChange={codeMirrorOnChange}> </CodeMirror>
        )
    }
})

LocateContent.CodeMirror = CodeMirror
export default LocateContent as typeof LocateContent & {
    readonly CodeMirror: typeof CodeMirror
}
