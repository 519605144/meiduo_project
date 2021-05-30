#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   jinja2_env.py    
@Contact :   519605144@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/5/28 10:25   huanghao      1.0         None
'''
from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from jinja2 import Environment


def environment(**options):
       env = Environment(**options)
       env.globals.update({
              'static': staticfiles_storage.url,
              'url': reverse,
       })
       return env