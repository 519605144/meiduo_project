#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   utils.py    
@Contact :   519605144@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/6/3 15:56   huanghao      1.0         None
'''
from django.contrib.auth.backends import ModelBackend
from django.db.models import Q

from apps.users.models import User

class UsernameMobileCheckBackend(ModelBackend):
       def authenticate(self, request, username=None, password=None, **kwargs):
              try:
                     user = User.objects.get(Q(mobile=username) | Q(username=username))
              except User.DoesNotExist:
                     return None

              if user.check_password(password):
                     return user