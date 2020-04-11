#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Mosson"
# 自定义异常的处理
import logging

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.db import DatabaseError
from redis import RedisError

logger = logging.getLogger("django")


def custom_exception_handler(exc, context):
    """
    自定义异常处理
    :param exc:  本次请求发生的异常信息
    :param context:  本清请求发送异常的执行上下文[ 本次请求的request对象，异常发送的时间，行号等... ]
    :return:
    """
    response = exception_handler(exc, context)

    if response is None:
        """来到这里只有2种情况：要么程序没出错，要么就是出错了而django或者restframework不识别"""
        view = context["view"]
        if isinstance(exc, DatabaseError) or isinstance(exc, RedisError):
            # 数据库异常
            logger.error('[%s] %s' % (view, exc))
            response = Response({'message': '服务器内部错误，请联系客服工作人员！'}, status=status.HTTP_507_INSUFFICIENT_STORAGE)

    return response