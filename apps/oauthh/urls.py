#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   urls.py    
@Contact :   519605144@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/6/4 15:33   huanghao      1.0         None
'''
from django.urls import path
from . import views
urlpatterns = [
       path('oauth_callback/',  views.OauthQQURLView.as_view(), name='callback')
]