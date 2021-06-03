#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   urls.py    
@Contact :   519605144@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/5/31 17:52   huanghao      1.0         None
'''
from django.urls import path
from . import views

urlpatterns = [
       path('', views.IndexViews.as_view(), name='contents'),
       path('index/', views.IndexViews.as_view(), name='index'),
]