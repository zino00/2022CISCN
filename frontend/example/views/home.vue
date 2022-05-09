<template>
    <mi-layout>
    </mi-layout>
</template>

<script lang="ts">
    import { defineComponent, createVNode } from 'vue'
    import {
        ThunderboltOutlined,LoginOutlined,ScheduleOutlined,
         GithubOutlined, AppstoreAddOutlined, SnippetsOutlined
    } from '@ant-design/icons-vue'

    export default defineComponent({
        created() {
            // 默认检测结果为 空
            this.$g.locatemenus.items = []
            this.$g.menus.dropdown = [{
                name: 'github',
                title: 'Github',
                path: 'https://github.com/Kiprey/2022CISCN',
                icon: createVNode(GithubOutlined),
                tag: {content: 'Hot'}
            }]
            this.$g.menus.items = [{
                name: 'start',
                path: '/start',
                meta: {
                    title: '项目简介',
                    subTitle: 'Getting Started',
                    icon: createVNode(ThunderboltOutlined),
                    tag: {color: '#f50', content: 'Hot'}
                },
            },{
                name: 'detect',
                path: '/pages',
                meta: {
                    title: '漏洞检测',
                    subTitle: 'Vulnerability Detection',
                    icon: createVNode(SnippetsOutlined)
                },
                children: [{
                    name: 'pages-submit',
                    path: '/pages/submit',
                    meta: {
                        title: '文件提交',
                        subTitle: 'submit',
                        icon: createVNode(LoginOutlined)
                    }
                }, {
                    name: 'pages-detect',
                    path: '/pages/detect',
                    meta: {
                        title: '漏洞定位',
                        subTitle: 'detect',
                        icon: createVNode(ScheduleOutlined)
                    }
                }]
            }, {
                name: 'about',
                path: '/pages/about',
                meta: {
                    title: '关于',
                    subTitle: 'about',
                    icon: createVNode(AppstoreAddOutlined),
                }
                }
            ]
        }
    })
</script>