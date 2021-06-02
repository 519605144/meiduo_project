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


@app.task
def send_sms_code(mobile, code):
       CCP().send_template_sms(mobile, [code, 5], 1)
