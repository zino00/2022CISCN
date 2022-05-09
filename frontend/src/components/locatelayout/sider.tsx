import { defineComponent } from 'vue'
import { Layout } from 'ant-design-vue'
import { useStore } from 'vuex'
import PropTypes, { getSlotContent } from '../../utils/props'
import LocateLayoutSiderMenu from '../locatemenu'

const LocateLayoutSider = defineComponent({
    name: 'LocateLayoutSider',
    props: {
        logo: PropTypes.any,
        menu: PropTypes.any,
        changeCodeMirror: PropTypes.func
    },
    setup() {
        const init = true
        const store = useStore()
        return { store, init }
    },
    methods: {
        getPrefixCls() {
            return this.$tools.getPrefixCls('layout-sider')
        },
        getLogoElem() {
            let logo = getSlotContent(this, 'logo')
            if (logo === undefined && !this.$g.mobile) logo = (<div style=" \
                    display: -webkit-box;   \
                    display: -ms-flexbox;   \
                    display: flex;  \
                    -webkit-box-align: center;  \
                    -ms-flex-align: center; \
                    align-items: center;    \
                    -webkit-box-pack: center;    \
                    -ms-flex-pack: center;   \
                    justify-content: center; \
                    position: relative; \
                    width: 16rem; \
                    height: 4rem; \
                    top: 0; \
                    left: 0; \
                    overflow: hidden; \
                    white-space: nowrap; \
                    cursor: pointer; \
                    padding-left: 0.5rem; \
                    padding-right: 0.5rem; \
                    text-overflow: ellipsis; \
                    color: var(--mi-header-logo-text-color, #f6ca9d); \
                    -webkit-transition: all 0.3s ease; \
                    transition: all 0.3s ease; \
                    z-index: 19900302; \
                    background: var(--mi-header-logo-bg-color, #1d1e23); \
                    border-bottom: 1px solid var(--mi-header-logo-border-bottom-color, #232427); \
                    // position: fixed; \
                    ">文件管理</div>)

            return logo
        },
        getMenuElem() {
            let menu = getSlotContent(this, 'menu')
            if (menu === undefined) {
                menu = (<LocateLayoutSiderMenu 
                    changeCodeMirror={this.changeCodeMirror} 
                    style="height: calc(100vh - 4rem); width: 16rem;"
                    items={this.$g.locatemenus.items}>
                </LocateLayoutSiderMenu>)
            }
            return menu
        },
    },
    render() {
        const prefixCls = this.getPrefixCls()
        return (
            <Layout.Sider
                class={prefixCls}
                width="256"
                >
                { this.getLogoElem() }
                { this.getMenuElem() }
            </Layout.Sider>
        )
    }
})

export default LocateLayoutSider