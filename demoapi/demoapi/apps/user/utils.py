
def jwt_response_payload_handler(token, user=None, request=None):
    """
    自定义jwt认证成功的返回结果
    :param token:   登录成功返回的jwt
    :param user:    登录成功的用户模型信息
    :param request: 本次客户端的请求对象
    :return:
    """
    return {
        "token": token,
        "id": user.id,
        "username": user.username
    }