from django.shortcuts import render

# Create your views here.
from django.views import View
from django import http

class OauthQQURLView(View):
       def get(self, request):
              #https://graph.qq.com/oauth2.0/authorize?response_type=code&cliend_id=101518219&redirect_id=127.0.0.1:8000/oauth_callback&state=test
              return http.JsonResponse({'login_url': 'www.baidu.com'})
