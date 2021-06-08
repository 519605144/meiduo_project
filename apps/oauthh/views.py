from QQLoginTool.QQtool import OAuthQQ
from django.contrib.auth import login
from django.shortcuts import render, redirect

# Create your views here.
from django.urls import reverse
from django.views import View
from django import http

from apps.oauthh.models import OAuthQQUser
from apps.oauthh.utils import generate_access_token, get_access_token
from apps.users.models import User
from meiduo_project import settings

class OauthQQURLView(View):
    def get(self, request):
        state = 'test'
        qqoauth = OAuthQQ(
            client_secret=settings.QQ_CLIENT_SECRET,
            client_id=settings.QQ_CLIENT_ID,
            redirect_uri=settings.QQ_REDIRECT_URL,
            state=state
        )
        # token = qqoauth.get_access_token(code)
        login_url = qqoauth.get_qq_url()
        # https://graph.qq.com/oauth2.0/authorize?response_type=code&cliend_id=101518219&redirect_id=127.0.0.1:8000/oauth_callback&state=test
        return http.JsonResponse({'login_url': login_url})


class OauthQQUserView(View):
    def get(self, request):
        #获得code
        code = request.GET.get('code')
        if code is None:
            return render(request, 'oauth_callback.html', context={'errmsg': '没有获取到code'})
        qqoauth = OAuthQQ(
            client_secret=settings.QQ_CLIENT_SECRET,
            client_id=settings.QQ_CLIENT_ID,
            redirect_uri=settings.QQ_REDIRECT_URL,
        )
        #通过code获得token
        token = qqoauth.get_access_token(code)
        #通过token获得唯一openid
        openid = qqoauth.get_open_id(token)

        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist as e:
            access_token = generate_access_token(openid=openid)
            return render(request, 'oauth_callback.html', context={'acccess_token': access_token})

        else:
            # 绑定过的直接登陆，然后回转首页
            response = redirect(reverse('index'))
            login(request, qquser.user)
            response.set_cookie('username', qquser.user.username, max_age=14*24*3600)


            return response

        return render(request, 'oauth_callback.html')

    def post(self, request):
        # 获取post请求中的信息
        data = request.POST
        mobile = data.get('phone')
        password = data.get('pwd')
        accesstoken = data.get('access_token')

        # access_token转码
        openid = get_access_token(accesstoken)

        #判断是否注册
        try:
            user = User.objects.get('mobile')
        except User.DoesNotExist as e:
            # 未绑定创建用户
            user = User.objects.create_user(
                username=mobile,
                password=password,
                mobile=mobile,
            )
        else:
            if not user.check_password(password):
                return http.HttpResponseBadRequest('已绑定用户,密码错误')
            #登录并保持状态
        qquser = OAuthQQUser.objects.create(
            user=user,
            openid=openid,
        )
        login(request, user)
        response = redirect(reverse('index'))
        response.set_cookie('username', user.username, max_age=14*3600*24)
        return response

