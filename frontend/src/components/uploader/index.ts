import Uploader from './uploader'
import { App, Plugin } from 'vue'

Uploader.install = function (app: App) {
    app.component(Uploader.name, Uploader)
    return app
}

export default Uploader as typeof Uploader & Plugin
