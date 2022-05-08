import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'

const Home = () => import('../views/home.vue')
const Login = () => import('../views/login.vue')
const Register = () => import('../views/register.vue')
const Start = () => import('../views/start.vue')
const Pages = () => import('../views/pages/index.vue')
const PagesLogin = () => import('../views/pages/login.vue')
const PagesRegister = () => import('../views/pages/register.vue')
const PagesLocate =() =>import('../views/pages/locate.vue')
const PagesSubmit =() =>import('../views/pages/submit.vue')
const PagesAbout =() =>import('../views/pages/about.vue')

const menuRoutes: Array<RouteRecordRaw> = [{
    path: '/',
    meta: {title: '首页'},
    component: Home,
    redirect: 'start',
    children: [{
        path: 'start',
        name: 'start',
        meta: {title: '项目简介'},
        component: Start,
    }, {
        path: 'pages',
        name: 'pages',
        meta: {title: '漏洞检测'},
        component: Pages,
        redirect: '/pages/submit',
        children: [{
            path: '/pages/submit',
            name: 'pages-submit',
            meta: {title: '文件提交'},
            component: PagesSubmit
        }, {
            path: '/pages/detect',
            name: '/pages-detect',
            meta: {title: '漏洞定位'},
            component: PagesLocate
        },{
            path: '/pages/about',
            name: '/pages-about',
            meta: {title: '关于'},
            component: PagesAbout
        }]
    }]
}]

const passportRoutes: Array<RouteRecordRaw> = [{
    path: '/login',
    name: 'single-login',
    meta: {title: '登录'},
    component: Login
}, {
    path: '/register',
    name: 'single-register',
    meta: {title: '注册'},
    component: Register
}]

const routes: Array<RouteRecordRaw> = [
    ...passportRoutes,
    ...menuRoutes
]

const router = createRouter({
    history: createWebHistory(),
    routes
})
export default router