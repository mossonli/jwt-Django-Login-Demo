// The Vue build version to load with the `import` command
// (runtime-only or standalone) has been set in webpack.base.conf with an alias.
import Vue from 'vue'
import App from './App'
import router from './router'

import settings from "./settings";

Vue.config.productionTip = false

// 将settings.js文件变成vue的属性，可以直接调用
Vue.prototype.$settings = settings

import axios from 'axios'
axios.defaults.withCredentials = false // 允许ajax携带cookie
Vue.prototype.$axios = axios // 将axios挂载到Vue上

// element-ui 配置
import ElementUI from "element-ui"
import 'element-ui/lib/theme-chalk/index.css'
Vue.use(ElementUI) // 将element-ui应用到vue的组件中

/* eslint-disable no-new */
new Vue({
  el: '#app',
  router,
  components: { App },
  template: '<App/>'
})
