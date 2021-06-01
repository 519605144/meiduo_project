#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   urls.py    
@Contact :   519605144@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/6/1 15:44   huanghao      1.0         None
'''
from django.urls import path
from . import views

urlpatterns = [
       path('image_codes/<uuid>/', views.VerificationView.as_view(), name='verification'),
       path('sms_code/<mobile>/', views.SmsCodeView.as_view(), name='smscode')
]