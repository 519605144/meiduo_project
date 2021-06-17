import json
import re

from django import http
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect
from logging import getLogger
# Create your views here.
from django.urls import reverse
from django.views import View
from django.contrib.auth.models import AbstractUser
from django_redis import get_redis_connection

from apps.oauthh.utils import get_access_token
from apps.users.models import User, Address
from apps.users.utils import generate_email_url, get_email_token
from apps.verification.views import logger
from meiduo_project import settings
from utils.response_code import RETCODE
from utils.views import LoginRequiredJSONMixin


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
                     # messages.warning(request, '参数有问题')
                     return render(request, 'login.html', context={'err_msg': '参数有问题'})

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

                     # 如果有next属性直接跳转next的网页
                     next_url = request.GET.get('next')
                     if next_url:
                            response = redirect('%s' % reverse(next_url.replace('/', '')))
                     else:
                            response = redirect(reverse('contents'))
                     # 设置cookie
                     response.set_cookie('username', user.username, max_age=14 * 24 * 3600)

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


class UserCenterInfoView(LoginRequiredMixin, View):
       def get(self, request):
              context = {
                     'username': request.user.username,
                     'mobile': request.user.mobile,
                     'email': request.user.email,
                     'email_active': request.user.email_active,
              }
              return render(request, 'user_center_info.html', context=context)


class EmailView(LoginRequiredJSONMixin, View):
       def get(self, request):
              # 1.接收Email数据
              data = json.loads(request.body.decode())
              email = data['email']
              # 2.验证数据
              if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$', email):
                     return http.JsonResponse({'code': RETCODE.PARAMERR, 'errmsg': '参数错误'})
              # 3.保存数据
              try:
                     request.user.email = email
                     request.user.save()
              except Exception as e:
                     return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': '数据库错误'})
              # 4.发送激活邮件
              from celery_task.send_email.tasks import send_email
              active_url = generate_email_url(request.user.id, email)
              send_email.delay(email, active_url, request.user.username)
              return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})


class EmailActiveView(View):
       def get(self, request):
              data = request.GET
              token = data.get('token')
              user = get_email_token(token)
              if user is None:
                     return http.HttpResponseBadRequest('用户不存在')
              user.email_active = True
              user.save()
              return redirect(reverse('center'))
"""
增加
1.接收数据
2.验证数据
3.数据入库
4.返回响应

删除
1.获取id
2.查询数据
3.删除
4.返回

修改
1.获取id
2.id查询
3.接收前端数据
4.数据验证
5.入库
6.返回响应 

查询
1.根据条件查询
2.对象转换列表
3.返回
"""
class AddressView(View):
       # 增加
       # 1.
       # 接收数据
       def get(self, request):
              addresses = Address.objects.filter(user=request.user, is_deleted=False)

              address_list = []
              for address in addresses:
                     address_list.append({
                     'id' : address.id,
                     'title' : address.title,
                     'receiver': address.receiver,
                     'province' : address.province.name,
                     'province_id' : address.province_id,
                     'city' : address.city.name,
                     'city_id' : address.city_id,
                     'district' : address.district.name,
                     'district_id' : address.district_id,
                     'place' : address.place,
                     'mobile' : address.mobile,
                      'tel' : address.tel,
                     'email' : address.email
                     })
              context = {
                     'addresses': address_list,
                     'default_address_id': request.user.default_address_id
              }

              return render(request, 'user_center_site.html', context=context)


       def post(self, request):

              count = request.user.add_user.all().count()
              if count>=20:
                     return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '地址不可以超过20个'})

              json_dict = json.loads(request.body.decode())
              receiver = json_dict.get('receiver')
              province_id = json_dict.get('province_id')
              city_id = json_dict.get('city_id')
              district_id = json_dict.get('district_id')
              place = json_dict.get('place')
              mobile = json_dict.get('mobile')
              tel = json_dict.get('tel')
              email = json_dict.get('email')

              # 2.
              # 验证数据
              if not all([receiver, province_id, city_id, district_id, place, mobile]):
                     return http.HttpResponseBadRequest('缺少必要参数')
              if not re.match(r'^1[345789]\d{9}$', mobile):
                     return http.HttpResponseBadRequest('mobile参数有误')
              if tel:
                     if not re.match(r'^(0[0-9]{2,3}-)?([2-9][0-9]{6,7})+(-[0-9]{1,4})?$', tel):
                            return http.HttpResponseBadRequest('tel参数有误')
              if email:
                     if not re.match(r'^[a - z0 - 9][\w\.\-] * @ [a - z0 - 9\-]+(\.[a-z]{2, 5}){1, 2}$', email):
                            return http.HttpResponseBadRequest('email参数有误')


              # 3.
              # 数据入库
              try:
                     address = Address.objects.create(
                            user = request.user,
                            title = receiver,
                            province_id=province_id,
                            city_id = city_id,
                            district_id = district_id,
                            place = place,
                            mobile = mobile,
                            tel = tel,
                            email = email,
                     )
                     if not request.user.default_address:
                            request.user.default_address = address
                            request.user.save()
              except Exception as e:
                     logger.error(e)
                     return http.HttpResponseBadRequest({'code': RETCODE.DBERR, 'errmsg': '新增地址失败'})

              # 4.
              # 返回响应
              address_dict = {
                     'id' : address.id,
                     'title' : address.title,
                     'receiver': address.receiver,
                     'province_id' : address.province_id,
                     'city_id' : address.city_id,
                     'district_id' : address.district_id,
                     'place' : address.place,
                     'mobile' : address.mobile,
                      'tel' : address.tel,
                     'email' : address.email
              }


              return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '新增地址成功', 'address': address_dict})
