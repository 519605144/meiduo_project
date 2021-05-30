from django.shortcuts import render

# Create your views here.
from django.views import View
from django.contrib.auth.models import AbstractUser


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

    def get(self, request):
        return render(request, 'register.html')
