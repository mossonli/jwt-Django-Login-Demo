import Vue from 'vue'
import Router from 'vue-router'
import HelloWorld from '@/components/HelloWorld'

import Home from "../components/Home"
import Login from "../components/Login"

Vue.use(Router);

export default new Router({
  mode: "history", //避免 url中出现#
  routes: [
    {
      path: '/',
      name: 'Home',
      component: Home
    },{
      path: '/user/login',
      name: 'Login',
      component: Login
    }

  ]
})
