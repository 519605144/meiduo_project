from django.shortcuts import render

# Create your views here.
from django import http
from django.views import View
from django_redis import get_redis_connection

from libs.captcha.captcha import captcha
from libs.yuntongxun.sms import CCP
from utils.response_code import RETCODE

import logging
logger = logging.getLogger('log')

class VerificationView(View):
       def get(self, request, uuid):
              text, image = captcha.generate_captcha()
              redis_conn = get_redis_connection('code')
              redis_conn.setex('img_%s'%uuid, 120, text)

              return http.HttpResponse(image, content_type='image/jpeg')

class SmsCodeView(View):
       def get(self, request, mobile):
              # 获得参数
              image_code = request.GET.get('image_code')
              uuid = request.GET.get('image_code_id')

              #参数检查
              if not all([image_code, uuid, mobile]):
                     return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errmsg': '参数不齐'})

              # 连接redis获取数据
              try:
                     redis_conn = get_redis_connection('code')
                     redis_code = redis_conn.get('img_%s'%uuid)
              except Exception as e:
                     logger.error(e)
                     return http.JsonResponse({'code': RETCODE.DBERR, 'errmsg': 'redis数据库错误'})

              if redis_code is None:
                     return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errmsg': '验证码过期'})

              if redis_code.decode().lower() != image_code.lower():
                     return http.JsonResponse({'code': RETCODE.SMSCODERR, 'errmsg': '验证码错误'})

              send_flag = redis_conn.get('send_flag%s'%mobile)
              if send_flag:
                     return http.JsonResponse({'code': RETCODE.THROTTLINGERR, 'errmsg': '操作太频繁'})

              from random import randint
              code = '%06d'%randint(0, 999999)
              # redis管道提高效率
              pipe = redis_conn.pipeline()

              pipe.setex('sms_%s'%mobile, 300, code)
              pipe.setex('send_flag%s'%mobile, 60, 1)
              pipe.execute()
              # CCP().send_template_sms(mobile, [code, 5], 1)

              from celery_task.sms.tasks import send_sms_code
              send_sms_code.delay(mobile, code)

              return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok'})



