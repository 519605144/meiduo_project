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
from itsdangerous import TimedJSONWebSignatureSerializer as serialize
from apps.users.models import User
from meiduo_project import settings
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

class UsernameMobileCheckBackend(ModelBackend):
       def authenticate(self, request, username=None, password=None, **kwargs):
              try:
                     user = User.objects.get(Q(mobile=username) | Q(username=username))
              except User.DoesNotExist:
                     return None

              if user.check_password(password):
                     return user

def generate_email_url(id, email):
       s = serialize(secret_key=settings.SECRET_KEY, expires_in=3000)
       data = {
              'id': id,
              'email': email
       }
       result = s.dumps(data).decode()
       email_url = f'http://127.0.0.1:8000/active_email?token={result}'
       return email_url

def get_email_token(token):
    s = Serializer(secret_key=settings.SECRET_KEY, expires_in=3600)
    data = s.loads(token)

    email = data.get('email')
    id = data.get('id')

    try:
           user = User.objects.get(id=id, email=email)
    except User.DoesNotExist:
           return None
    return user