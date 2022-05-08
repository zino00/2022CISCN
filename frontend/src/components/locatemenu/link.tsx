import { defineComponent, isVNode } from 'vue'
import PropTypes from '../../utils/props'
import * as Icon from '@ant-design/icons-vue'

export default defineComponent({
    name: 'LocateMenuItemLink',
    props: {
        item: PropTypes.object.isRequired,
    },
    methods: {
        getPrefixCls() {
            return this.$tools.getPrefixCls('menu-item')
        },
        getIconElem() {
            const MenuIcon = Icon['SnippetsOutlined']
            return <MenuIcon></MenuIcon>
        },
        getTitleElem() {
            const prefixCls = this.getPrefixCls()
            const text = this.item.filepath
            let title: any = (
                    <div class={`${prefixCls}-title`}>
                        <span innerHTML={text}></span>
                    </div>
                )
            return title
        },
    },
    render() {
        return (
            <>
                { this.getIconElem()}
                { this.getTitleElem() }
            </>
        )
    }
})