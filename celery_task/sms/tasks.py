#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   tasks.py    
@Contact :   519605144@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/6/2 17:11   huanghao      1.0         None
'''
from celery_task.main import app
from libs.yuntongxun.sms import CCP


@app.task(bind=True, default_retry_delay=10)
def send_sms_code(self, mobile, code):
       try:
              result = CCP().send_template_sms(mobile, [code, 5], 1)
       except Exception as e:
              raise self.retry(exc=e, max_retries=10)
       if result == 0:
              raise self.retry(exc=Exception('重试'), max_retries=10)