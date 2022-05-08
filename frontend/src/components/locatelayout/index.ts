import { App, Plugin } from 'vue'
import Layout from './layout'

Layout.install = function (app: App) {
    app.component(Layout.name, Layout)
    app.component(Layout.Sider.name, Layout.Sider)
    app.component(Layout.Content.name, Layout.Content)
    // app.component(Layout.Footer.name, Layout.Footer)
    app.component('LocateCodeMirror', Layout.Content.CodeMirror)
    return app
}

export default Layout as typeof Layout & Plugin
