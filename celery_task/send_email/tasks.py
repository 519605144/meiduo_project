#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   tasks.py    
@Contact :   519605144@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/6/10 9:56   huanghao      1.0         None
'''
from apps.users.models import User
from apps.users.utils import generate_email_url
from celery_task.main import app
from meiduo_project import settings


@app.task(bind=True, default_retry_delay=10)
def send_email(self, email, active_url, username):
       from django.core.mail import send_mail
       subject = '美多商城激活邮件'
       message = ''
       html_message = f'<p>尊敬的用户{username}, 您好!' \
                 f'<p>{email}感谢您使用美多商城。' \
                 f'<p><a href="{active_url}">{active_url}</a>'
       # message = ''
       from_email = settings.EMAIL_FROM
       recipient_list = [email]
       try:
              result = send_mail(subject=subject,
                                 html_message=html_message,
                                 message=message,
                                 from_email=from_email,
                                 recipient_list=recipient_list)
       except Exception as e:
              raise self.retry(exc=e, max_retries=10)
       if result == 0:
              raise self.retry(exc=Exception('重试'), max_retries=10)
