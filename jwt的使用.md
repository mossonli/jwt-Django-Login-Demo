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

```vue
<button class="login_btn" @click="loginhander">登录</button>
# ......
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

