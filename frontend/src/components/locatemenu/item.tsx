import { defineComponent } from 'vue'
import { Menu } from 'ant-design-vue'
import { RouterLink } from 'vue-router'
import PropTypes from '../../utils/props'
import LocateMenuItemLink from './link'

export default defineComponent({
    name: 'LocateMenuItem',
    props: {
        item: PropTypes.object,
        changeCodeMirror: PropTypes.func,
    },
    methods: {
        getPrefixCls() {
            return this.$tools.getPrefixCls('menu-item')
        },
        getMenuItemElem() {
            const prefixCls = this.getPrefixCls()
            const testOnClick = () => {
                // console.log(this.item.code)
                this.changeCodeMirror(this.item.code, this.item.vuln)
            };
            let link: any = (
                <a class={`${prefixCls}-link`} onClick={testOnClick}
                        // target={this.item.meta.target ?? '_blank'}
                        >
                        <LocateMenuItemLink
                            item={this.item}>
                        </LocateMenuItemLink>
                    </a>
            )
            return link
        }
    },
    render() {
        const prefixCls = this.getPrefixCls()
        const key = this.$g.prefix + (this.item ? this.item.name : this.$tools.uid())
        return (
            <Menu.Item class={prefixCls} key={key}>
                { this.getMenuItemElem() }
            </Menu.Item>
        )
    }
})