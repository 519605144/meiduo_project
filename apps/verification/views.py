from django.shortcuts import render

# Create your views here.
from django import http
from django.views import View
from django_redis import get_redis_connection

from libs.captcha.captcha import captcha
from libs.yuntongxun.sms import CCP
from utils.response_code import RETCODE


class VerificationView(View):
       def get(self, request, uuid):
              text, image = captcha.generate_captcha()
              redis_conn = get_redis_connection('code')
              redis_conn.setex('img_%s'%uuid, 120, text)

              return http.HttpResponse(image, content_type='image/jpeg')

class SmsCodeView(View):
       def get(self, request, mobile):
              # 获得参数
              image_code = request.Get.get('image_code')
              uuid = request.Get.get('uuid')

              #参数检查
              if not all([image_code, uuid, mobile]):
                     return http.JsonResponse({'code': RETCODE.NECESSARYPARAMERR, 'errormsg': '参数不齐'})

              # 连接redis获取数据
              redis_conn = get_redis_connection('code')
              redis_code = redis_conn.get('img_%s'%mobile)

              if redis_code is None:
                     return http.JsonResponse({'code': RETCODE.IMAGECODEERR, 'errormsg': '验证码过期'})

              if redis_code != image_code:
                     return http.JsonResponse({'code': RETCODE.SMSCODERR, 'errormsg': '验证码错误'})

              from random import randint
              code = '%06d'%randint(0, 999999)
              redis_conn.setex('sms_%s'%mobile, 300, code)
              CCP().send_template_sms(mobile, [code, 5], 1)

              return http.JsonResponse({'code': RETCODE.OK, 'errormsg': 'ok'})

