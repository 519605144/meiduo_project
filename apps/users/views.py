import re

from django import http
from django.contrib.auth import login
from django.shortcuts import render, redirect
from logging import getLogger
# Create your views here.
from django.urls import reverse
from django.views import View
from django.contrib.auth.models import AbstractUser
from django_redis import get_redis_connection

from apps.users.models import User
from utils.response_code import RETCODE


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
              # 1.获取数据
              data = request.POST
              username = data.get('user_name')
              password = data.get('password')
              password2 = data.get('password2')
              mobile = data.get('phone')
              allow = data.get('error_allow')
              sms_code_client = data.get('msg_code')

              # 2.验证数据
              #   2.1 数据非空验证
              if not all([username, password, password2, mobile]):
                     return http.HttpResponseBadRequest('参数有问题')
              #   2.2 用户名判断
              re1 = r'^[a-zA-Z][a-zA-Z0-9_-]{4,19}$'
              if not re.match(re1, username):
                     return http.HttpResponseBadRequest('用户名有问题')
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
                     redis_conn = get_redis_connection('code')
                     sms_code_server = redis_conn.get('sms_%s' % mobile)
              except Exception as e:
                     self.logger.error(e)
                     return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'redis数据库错误'})

              if sms_code_server is None:
                     return render(request, '/register.html', {'sms_code_errmsg': '无效的短信验证码'})

              if sms_code_client != sms_code_server.decode():
                     return render(request, '/register.html', {'sms_code_errmsg': '短信验证码错误'})

              try:
                     user = User.objects.create_user(username=username, password=password, mobile=mobile)
              except:
                     self.logger.error()
                     return render(request, 'register.html', context={'error_message': '数据库异常'})
                     return http.HttpResponseBadRequest('数据库异常')

              from django.contrib.auth import login
              login(request, user)

              return redirect(reverse('contents'))


class UsernameCountView(View):

       def get(self, request, username):
              try:
                     count = User.objects.filter(username=username).count()
              except Exception as e:
                     logger = getLogger('log')
                     logger.error(e)
                     return http.JsonResponse({'code': 400, 'errmsg': '数据库异常'})

              return http.JsonResponse({'code': 0, 'count': count})


class MobileCountView(View):
       def get(self, request, mobile):
              try:
                     count = User.objects.filter(mobile=mobile).count()
              except Exception as e:
                     logger = getLogger('log')
                     logger.error(e)
                     return http.JsonResponse({'code': 400, 'errmsg': '数据库异常'})

              return http.JsonResponse({'code': 0, 'count': count})


class LoginView(View):
       def get(self, request):
              return render(request, 'login.html')

       def post(self, request):
              data = request.POST
              username = data.get('username')
              password = data.get('pwd')
              remember = data.get('remembered')

              if not all([username, password]):
                     return http.HttpResponseBadRequest('参数有问题')

              re1 = r'^[a-zA-Z0-9_-]{5,20}$'
              if not re.match(re1, username):
                     return http.HttpResponseBadRequest('用户名不符合规则')

              re2 = r'^[0-9A-Za-z]{8,20}$'
              if not re.match(re2, password):
                     return http.HttpResponseBadRequest('密码不符合规则')

              from django.contrib.auth import authenticate
              user = authenticate(username=username, password=password)


              if user is not None:
                     login(request, user)

                     if remember == 'on':
                            request.session.set_expiry(30 * 24 * 3600)
                     else:
                            request.session.set_expiry(0)
                     response = redirect(reverse('contents'))
                     # 设置cookie
                     response.set_cookie('username', user.username, max_age=14*24*3600)

                     return response

              else:
                     return render(request, 'login.html', context={'account_errmsg': '用户名或密码错误'})

class LogoutView(View):
       def get(self, request):
              from django.contrib.auth import logout
              logout(request)

              response = redirect(reverse('contents'))
              response.delete_cookie('username')
              return response
