# jwt-Django-Login-Demo

# 前后端分离跨域的处理

### 后端的处理方式

> 安装跨域插件

```python
> pip install django-cors-headers
```

> 修改django配置文件

```python
# 解决跨域的插件 1
INSTALLED_APPS = [
  	.......
    'corsheaders' # 相当于在Response(headers={"Access-Control-Allow-Origin":"客户端地址/*"})
		......
]
# 解决跨域的插件 2
CORS_ORIGIN_WHITELIST = (
    # 在部分的cors_headers模块中，如果不带协议会导致客户端无法跨域需要配置"http://www.luffycity.cn:8080"
    'www.luffycity.cn',
)
# 解决跨域的插件 3
CORS_ALLOW_CREDENTIALS = False # 阻止ajax跨域请求时携带cookie
#解决跨域的插件 4
MIDDLEWARE = [
    # 配合跨域的中间件【放在中间件的第一个位置】
    'corsheaders.middleware.CorsMiddleware' 
		......
]
```

### 前端的处理方式

> 安装跨域的前端插件

```vue
> npm install axios -S
```

> 在main.js中引用axios插件

```javascript
// 从node_modules目录中倒入包
import axios from 'axios'
axios.defaults.withCredentials = false // 阻止ajax携带cookie
Vue.prototype.$axios = axios // 将axios挂载到Vue上
```

