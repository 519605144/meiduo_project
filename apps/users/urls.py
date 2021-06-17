#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   urls.py    
@Contact :   519605144@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/5/28 17:11   huanghao      1.0         None
'''
from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
       path('register/', views.RegisterView.as_view(), name='register'),
       # url('usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/', views.UsernameCountView.as_view(), name='usernamecount'),
       path('usernames/<username>/count/', views.UsernameCountView.as_view(), name='usernamecount'),
       path('mobiles/<mobile>/count/', views.MobileCountView.as_view(), name='mobilecount'),
       path('login/', views.LoginView.as_view(), name='login'),
       path('logout/', views.LogoutView.as_view(), name='logout'),
       path('center/', views.UserCenterInfoView.as_view(), name='center'),
       path('emails/', views.EmailView.as_view(), name='email'),
       path('active_email/', views.EmailActiveView.as_view(), name='activeemail'),
       path('addresses/', views.AddressView.as_view(), name='showaddress'),

]