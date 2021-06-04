#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   models.py    
@Contact :   519605144@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/6/4 11:42   huanghao      1.0         None
'''
from django.db import models


class BaseModel(models.Model):
       create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
       update_time = models.DateTimeField(auto_now_add=True, verbose_name='更新时间')

       class Meta:
              abstract = True

