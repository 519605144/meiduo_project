import re

from django import http
from django.shortcuts import render, redirect
from logging import getLogger
# Create your views here.
from django.urls import reverse
from django.views import View
from django.contrib.auth.models import AbstractUser

from apps.users.models import User


class RegisterView(View):
    '''
       1. 用户名：第一位为英文，总长度5-20，不能全数字
       2. 密码：8-20位，必须包含数字，英文和特殊符号
       3. 确认密码： 与密码一致
       4. 手机号： 满足手机号要求，11位数字
       5. 图片验证码：captcha
       6. 短信发送
       7. 同意协议

       需要通过ajax与后台交互的：
       用户名， 手机号重复
       短信，图片验证码
       注册
       '''
    def __init__(self):
        self.logger = getLogger('log')

    def get(self, request):
        return render(request, 'register.html')

    def post(self, request):
        #1.获取数据
        data = request.POST
        username = data.get('user_name')
        password = data.get('password')
        password2 = data.get('password2')
        mobile = data.get('phone')
        allow = data.get('error_allow')

        #2.验证数据
        #   2.1 数据非空验证
        if not all([username, password, password2, mobile]):
            return http.HttpResponseBadRequest('参数有问题')
        #   2.2 用户名判断
        re1 = r'^[a-zA-Z][a-zA-Z0-9_-]{4,19}$'
        if not re.match(re1, username):
            return http.HttpResponseBadRequest('账户名有问题')
        #   2.3 密码判断
        re2 = r'^[0-9A-Za-z]{8,20}$'
        if not re.match(re2, password):
            return http.HttpResponseBadRequest('密码有问题')
        #   2.4 密码一致判断
        if password != password2:
            return http.HttpResponseBadRequest('密码不一致')
        #   2.5  手机号判断
        re3 = r'^1[345789]\d{9}$'
        if not re.match(re3, mobile):
            return http.HttpResponseBadRequest('手机号有问题')

        # 2.6 协议判断
        # if allow != 'on':
        #     print(allow)
        #     return http.HttpResponseBadRequest('协议未勾选')
        try:
            user = User.objects.create_user(username=username, password=password, mobile=mobile)
        except:
            self.logger.error()
            return render(request, 'register.html', context={'error_message':'数据库异常'})
            return http.HttpResponseBadRequest('数据库异常')

        return redirect(reverse('contents'))

