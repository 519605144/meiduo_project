#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   urls.py    
@Contact :   519605144@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/6/15 10:48   huanghao      1.0         None
'''
from django.urls import path
from . import views

urlpatterns = [
       path('areas/', views.CityiViews.as_view(), name='city'),
]