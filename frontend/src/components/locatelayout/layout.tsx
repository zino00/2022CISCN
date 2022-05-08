import { defineComponent } from 'vue'
import { useStore } from 'vuex'
import { Layout, BackTop } from 'ant-design-vue'
import PropTypes, { getSlotContent } from '../../utils/props'
import { mutations } from '../../store/types'
// import LocateLayoutHeader from './header'
import LocateLayoutSider from './sider'
import LocateLayoutContent from './content'
import LocateLayoutFooter from './footer'
import MiMenuDrawer from '../menu/drawer'

const LocateLayout = defineComponent({
    name: 'LocateLayout',
    props: {
        embed: PropTypes.bool,
        siderClassName: PropTypes.string,
        menuClassName: PropTypes.string,
        sider: PropTypes.any,
        header: PropTypes.any,
        headerExtra: PropTypes.any,
        footer: PropTypes.any
    },
    computed: {
        hasSider() {
            return this.$g.mobile ? false : true
        },
        layoutClass() {
            let layoutClass = this.$tools.getPrefixCls('layout')
            const themeClass = this.$tools.getPrefixCls('theme')
            layoutClass += this.$g.embed ? ` ${layoutClass}-embed`: ''
            layoutClass += this.$g.mobile ? ` ${layoutClass}-mobile` : ''
            layoutClass += this.$g.theme === 'dark'
                ? ` ${themeClass}-dark`
                : this.$g.theme === 'light'
                    ? ` ${themeClass}-light`
                    : ''
            return layoutClass
        }
    },
    setup() {
        const store = useStore()
        return { store }
    },
    created() {
        if (this.$g.mobile) {
            this.$g.menus.collapsed = false
            this.store.commit(`layout/${mutations.layout.collapsed}`, false)
        }
    },
    methods: {
        getSiderElem() {
            let sider = getSlotContent(this, 'sider')
            if (sider === undefined) sider = <LocateLayoutSider changeCodeMirror={this.changeCodeMirror}></LocateLayoutSider>
            if (this.$g.mobile || this.embed) sider = null
            return sider
        },
        // getFooterElem() {
        //     let footer = getSlotContent(this, 'footer')
        //     if (footer === undefined) footer = <LocateLayoutFooter></LocateLayoutFooter>
        //     return footer
        // },
        getLayoutElem() {
            const prefixCls = this.$tools.getPrefixCls('layout')
            return (
                <>
                    { this.getSiderElem() }
                    <Layout class={`${prefixCls}-container`} hasSider={false}>
                        <LocateLayoutContent ref="locate_layout_content"></LocateLayoutContent>
                        {/* { this.getFooterElem() } */}
                    </Layout>
                </>
            )
        },
        changeCodeMirror(newCode, vulns) {
            this.$refs.locate_layout_content.update(newCode, vulns)
            // this.$refs.locate_layout_content.code = newCode
            // this.$refs.locate_layout_content.vulns = vulns
            // console.log("changeCodeMirror ", 
            //     this.$refs.locate_layout_content.code, 
            //     this.$refs.locate_layout_content.vulns);
            // this.$refs.locate_layout_content.$forceUpdate()
        }
    },
    render() {
        const drawer = this.$g.mobile ? <MiMenuDrawer></MiMenuDrawer> : null
        return (
            <>
                <Layout hasSider={this.hasSider} class={this.layoutClass}>
                    { this.getLayoutElem() }
                    { this.$g.backToTop ? <BackTop target={() => document.body}></BackTop> : null }
                </Layout>
                { drawer }
            </>
        )
    }
})
// LocateLayout.Header = LocateLayoutHeader
LocateLayout.Sider = LocateLayoutSider
LocateLayout.Sider.Logo = LocateLayoutSider.Logo
LocateLayout.Content = LocateLayoutContent
// LocateLayout.Footer = LocateLayoutFooter
export default LocateLayout as typeof LocateLayout & {
    readonly Sider: typeof LocateLayoutSider
    // readonly Header: typeof LocateLayoutHeader
    readonly Content: typeof LocateLayoutContent
    // readonly Footer: typeof LocateLayoutFooter
}

{/* <template>
    <LocateLayout></LocateLayout>
</template> */}