#!/usr/bin/env python
# -*- encoding: utf-8 -*-
'''
@File    :   main.py    
@Contact :   519605144@qq.com
@License :   (C)Copyright 2017-2018, Liugroup-NLPR-CASIA

@Modify Time      @Author    @Version    @Desciption
------------      -------    --------    -----------
2021/6/2 16:30   huanghao      1.0         None
'''

# 1. 创建celery
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", 'meiduo_project.settings')
from celery import Celery

app = Celery('celery_task')

# 2. 设置队列broker
app.config_from_object('celery_task.config')

# 3. 设置生产者task（必须用task实例对象的装饰器）
app.autodiscover_tasks(['celery_task.sms', 'celery_task.send_email'])

# 4. 设置消费者worker
