# Django中使用jwt

> 安装

```python
pip install djangorestframework-jwt
```

> settings/dev.py的配置

```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_jwt.authentication.JSONWebTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ),
}
import datetime
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
}
```

## 手动生成jwt

```python
from rest_framework_jwt.settings import api_settings

jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER

payload = jwt_payload_handler(user)
token = jwt_encode_handler(payload)
```

## Django项目中使用jwt进行登录认证

> 后端

主路由

```python
urlpatterns = [
		...
    path('user/', include("users.urls")),
    # include 的值必须是 模块名.urls 格式,字符串中间只能出现一个圆点
]
```

子路由

```python
from rest_framework_jwt.views import obtain_jwt_token

urlpatterns = [
    path(r'login/', obtain_jwt_token),
]
```

测试

```html
使用接口测试工具(postman)，访问登录接口
127.0.0.1:8000/user/login/
```

> 前端

登录页面,绑定点击事件

```Vue
<button class="login_btn" @click="loginhander">登录</button>

export default {
  name: 'Login',
  data(){
    return {
        login_type: 0,
        remember:false, // 记住密码
        username:"",
        password:"",
    }
  },

  methods:{
    // 登录
    loginhander(){
      this.$axios.post("http://127.0.0.1:8000/users/authorizations/",{"username":this.username,"password":this.password}).then(response=>{
        console.log(response.data)
      }).catch(error=>{
        console.log(error)
      })
    }
  },

};
```

至此，一个粗略的django and jwt的登录示例就已经完成了

### 调优部分

> 前端保存jwt

- **sessionStorage** 浏览器关闭即失效
- **localStorage** 长期有效

```vue
sessionStorage.变量名 = 变量值   // 保存数据
sessionStorage.setItem("变量名","变量值") // 保存数据
sessionStorage.变量名  // 读取数据
sessionStorage.getItem("变量名") // 读取数据
sessionStorage.removeItem("变量名") // 清除单个数据
sessionStorage.clear()  // 清除所有sessionStorage保存的数据

localStorage.变量名 = 变量值   // 保存数据
localStorage.setItem("变量名","变量值") // 保存数据
localStorage.变量名  // 读取数据
localStorage.getItem("变量名") // 读取数据
localStorage.removeItem("变量名") // 清除单个数据
localStorage.clear()  // 清除所有sessionStorage保存的数据
```

登陆组件代码Login.vue

```vue
// 使用浏览器本地存储保存token
  if (this.remember) {
    // 记住登录
    sessionStorage.clear();
    localStorage.token = response.data.token;
  } else {
    // 未记住登录
    localStorage.clear();
    sessionStorage.token = response.data.token;
  }
	// 页面跳转回到上一个页面 也可以使用 this.$router.push("/") 回到首页
	this.$router.go(-1)
```

默认的返回值仅有token，我们还需在返回值中增加username和id，方便在客户端页面中显示当前登陆用户

通过修改该视图的返回值可以完成我们的需求。

在user/utils.py 中，创建

```python
def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功返回数据
    """
    return {
        'token': token,
        'id': user.id,
        'username': user.username
    }
```

修改settings/dev.py配置文件

```python
# JWT
JWT_AUTH = {
    'JWT_EXPIRATION_DELTA': datetime.timedelta(days=1),
    'JWT_RESPONSE_PAYLOAD_HANDLER': 'user.utils.jwt_response_payload_handler',
}
```

登陆组件代码Login.vue

```javascript
// 使用浏览器本地存储保存token
  if (this.remember) {
    // 记住登录
    sessionStorage.clear();
    localStorage.token = response.data.token;
    localStorage.id = response.data.id;
    localStorage.username = response.data.username;
  } else {
    // 未记住登录
    localStorage.clear();
    sessionStorage.token = response.data.token;
    sessionStorage.id = response.data.id;
    sessionStorage.username = response.data.username;
  }
```

## 多条件登录

JWT扩展的登录视图，在收到用户名与密码时，也是调用Django的认证系统中提供的**authenticate()**来检查用户名与密码是否正确。

我们可以通过修改Django认证系统的认证后端（主要是authenticate方法）来支持登录账号既可以是用户名也可以是手机号。

**修改Django认证系统的认证后端需要继承django.contrib.auth.backends.ModelBackend，并重写authenticate方法。**

`authenticate(self, request, username=None, password=None, **kwargs)`方法的参数说明：

- request 本次认证的请求对象
- username 本次认证提供的用户账号
- password 本次认证提供的密码

**我们想要让用户既可以以用户名登录，也可以以手机号登录，那么对于authenticate方法而言，username参数即表示用户名或者手机号。**

重写authenticate方法的思路：

1. 根据username参数查找用户User对象，username参数可能是用户名，也可能是手机号
2. 若查找到User对象，调用User对象的check_password方法检查密码是否正确

在users/utils.py中编写：

```python
def get_user_by_account(account):
    """
    根据帐号获取user对象
    :param account: 账号，可以是用户名，也可以是手机号
    :return: User对象 或者 None
    """
    try:
        if re.match('^1[3-9]\d{9}$', account):
            # 帐号为手机号
            user = User.objects.get(mobile=account)
        else:
            # 帐号为用户名
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        return None
    else:
        return user

import re
from .models import User
from django.contrib.auth.backends import ModelBackend
class UsernameMobileAuthBackend(ModelBackend):
    """
    自定义用户名或手机号认证
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)
        if user is not None and user.check_password(password):
            return user
```

在配置文件settings/dev.py中告知Django使用我们自定义的认证后端

```python
AUTHENTICATION_BACKENDS = [
    'user.utils.UsernameMobileAuthBackend',
]
```

> 前端首页实现登录状态的判断

Common/Header.vue

```javascript
<template>
    <div class="header-box">
      <div class="header">
        <div class="content">
          <div class="logo full-left">
            <router-link to="/"><img src="/static/image/logo.svg" alt=""></router-link>
          </div>
          <ul class="nav full-left">
              <li v-for="nav in nav_list">
                <span v-if="nav.is_site"><a :href="nav.link">{{nav.title}}</a></span>
                <span v-else><router-link :to="nav.link">{{nav.title}}</router-link></span>
              </li>
          </ul>

          <div class="login-bar full-right">
            <div class="shop-cart full-left">
              <span class="shop-cart-total">0</span>
              <img src="/static/image/cart.svg" alt="">
              <span><router-link to="/cart">购物车</router-link></span>
            </div>
            <div class="login-box login-box1 full-left">
              <router-link to="">学习中心</router-link>
              <el-menu width="200" class="member el-menu-demo" mode="horizontal">
                  <el-submenu index="2">
                    <template slot="title"><img src="/static/image/logo@2x.png" alt=""></template>
                    <el-menu-item index="2-1">我的账户</el-menu-item>
                    <el-menu-item index="2-2">我的订单</el-menu-item>
                    <el-menu-item index="2-3">我的优惠卷</el-menu-item>
                    <el-menu-item index="2-3"><span>退出登录</span></el-menu-item>
                  </el-submenu>
                </el-menu>
            </div>
          </div>

          <div v-if="token" class="login-bar full-right">
            <div class="shop-cart full-left">
              <img src="/static/image/cart.svg" alt="">
              <span><router-link to="/cart">购物车</router-link></span>
            </div>
            <div class="login-box full-left">
              <router-link to="/user/login">登录</router-link>
              &nbsp;|&nbsp;
              <span>注册</span>
            </div>
          </div>

        </div>
      </div>
    </div>
</template>



<style scoped>
...

.header .login-bar .shop-cart{
  margin-right: 20px;
  border-radius: 17px;
  background: #f7f7f7;
  cursor: pointer;
  font-size: 14px;
  height: 28px;
  width: 90px;
  margin-top: 30px;
  line-height: 32px;
  text-align: center;
}
    
.member{
    display: inline-block;
    height: 34px;
    margin-left: 20px;
}
.member img{
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: inline-block;
}
.member img:hover{
  border: 1px solid yellow;
}
.header .login-bar .login-box1{
  margin-top: 16px;
}
</style>
```

> 推出登录

```javascript
<template>
    <div class="header-box">
      <div class="header">
        <div class="content">
          <div class="logo full-left">
            <router-link to="/"><img src="/static/image/logo.svg" alt=""></router-link>
          </div>
          <ul class="nav full-left">
              <li v-for="nav in nav_list">
                <span v-if="nav.is_site"><a :href="nav.link">{{nav.title}}</a></span>
                <span v-else><router-link :to="nav.link">{{nav.title}}</router-link></span>
              </li>
          </ul>

          <div v-if="token" class="login-bar full-right">
            <div class="shop-cart full-left">
              <span class="shop-cart-total">0</span>
              <img src="/static/image/cart.svg" alt="">
              <span><router-link to="/cart">购物车</router-link></span>
            </div>
            <div class="login-box login-box1 full-left">
              <router-link to="">学习中心</router-link>
              <el-menu width="200" class="member el-menu-demo" mode="horizontal">
                  <el-submenu index="2">
                    <template slot="title"><img src="/static/image/logo@2x.png" alt=""></template>
                    <el-menu-item index="2-1">我的账户</el-menu-item>
                    <el-menu-item index="2-2">我的订单</el-menu-item>
                    <el-menu-item index="2-3">我的优惠卷</el-menu-item>
                    <el-menu-item index="2-3"><span @click="logoutHander">退出登录</span></el-menu-item>
                  </el-submenu>
                </el-menu>
            </div>
          </div>

          <div v-else class="login-bar full-right">
            <div class="shop-cart full-left">
              <img src="/static/image/cart.svg" alt="">
              <span><router-link to="/cart">购物车</router-link></span>
            </div>
            <div class="login-box full-left">
              <router-link to="/user/login">登录</router-link>
              &nbsp;|&nbsp;
              <span>注册</span>
            </div>
          </div>

        </div>
      </div>
    </div>
</template>

<script>
    export default {
      name: "Header",
      data(){
        return{
            token:"",
            nav_list: [],
        }
      },
      created() {
          this.check_user_login();
          this.get_nav();
      },
      methods:{
          check_user_login(){
            // 获取用户的登录状态
            this.token = sessionStorage.user_token || localStorage.user_token;
            return this.token;
          },
          get_nav(){
              this.$axios.get(`${this.$settings.HOST}/nav/header/`,{}).then(response=>{
                  this.nav_list = response.data;
              }).catch(error=>{
                  console.log(error.response);
              })
          },
          logoutHander(){
              // 退出登录
              localStorage.removeItem("user_token");
              localStorage.removeItem("user_id");
              localStorage.removeItem("user_name");
              sessionStorage.removeItem("user_token");
              sessionStorage.removeItem("user_id");
              sessionStorage.removeItem("user_name");
              this.check_user_login();
          }
      }
    }
</script>

<style scoped>
.header-box{
  height: 80px;
}
.header{
  width: 100%;
  height: 80px;
  box-shadow: 0 0.5px 0.5px 0 #c9c9c9;
  position: fixed;
  top:0;
  left: 0;
  right:0;
  margin: auto;
  z-index: 99;
  background: #fff;
}
.header .content{
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}
.header .content .logo{
  height: 80px;
  line-height: 80px;
  margin-right: 50px;
  cursor: pointer; /* 设置光标的形状为爪子 */
}
.header .content .logo img{
  vertical-align: middle;
}
.header .nav li{
  float: left;
  height: 80px;
  line-height: 80px;
  margin-right: 30px;
  font-size: 16px;
  color: #4a4a4a;
  cursor: pointer;
}
.header .nav li span{
  padding-bottom: 16px;
  padding-left: 5px;
  padding-right: 5px;
}
.header .nav li span a{
  display: inline-block;
}
.header .nav li .this{
  color: #4a4a4a;
  border-bottom: 4px solid #ffc210;
}
.header .nav li:hover span{
  color: #000;
}
.header .login-bar{
  height: 80px;
}
.header .login-bar .shop-cart{
  margin-right: 20px;
  border-radius: 17px;
  background: #f7f7f7;
  cursor: pointer;
  font-size: 14px;
  height: 28px;
  width: 90px;
  margin-top: 30px;
  line-height: 32px;
  text-align: center;
}
.header .login-bar .shop-cart:hover{
  background: #f0f0f0;
}
.header .login-bar .shop-cart img{
  width: 15px;
  margin-right: 4px;
  margin-left: 6px;
}
.header .login-bar .shop-cart span{
  margin-right: 6px;
}
.header .login-bar .login-box{
  margin-top: 32px;
}
.header .login-bar .login-box span{
  color: #4a4a4a;
  cursor: pointer;
}
.header .login-bar .login-box span:hover{
  color: #000000;
}
.member{
    display: inline-block;
    height: 34px;
    margin-left: 20px;
}
.member img{
  width: 26px;
  height: 26px;
  border-radius: 50%;
  display: inline-block;
}
.member img:hover{
  border: 1px solid yellow;
}
.header .login-bar .login-box1{
  margin-top: 16px;
}
</style>
```

