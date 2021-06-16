import json

from django import http
from django.core.cache import cache
from django.shortcuts import render

# Create your views here.
from django.views import View

from apps.areas.models import Area
from utils.response_code import RETCODE


class CityiViews(View):
       # 网址为：/areas?parentid=
       # 若没有parentid就为市
       def get(self, request):
              data = request.GET
              parent_id = data.get('area_id')
              if parent_id is None:
                     province_list = cache.get('pro')
                     if province_list is None:
                            provinces = Area.objects.filter(parent=100000)
                            print(provinces)
                            # 得到province对象
                            province_list = []
                            for province in provinces:
                                   province_list.append({
                                          'id': province.id,
                                          'name': province.name
                                   })
                            cache.set('pro', province_list, 24*3600)

                     return http.JsonResponse({'code':RETCODE.OK, 'errmsg': 'ok', 'province_list': province_list}, json_dumps_params={'ensure_ascii':False})
              else:
                     # 市区
                     sub_data = cache.get(f'sub_{parent_id}')
                     if sub_data is None:
                            sub_areas = Area.objects.filter(parent=parent_id)
                            sub_data = []
                            for sub in sub_areas:
                                   sub_data.append({
                                          'id': sub.id,
                                          'name': sub.name
                                   })
                            cache.set(f'sub_{parent_id}', 24*3600)
                     return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'ok', 'sub_data': sub_data}, json_dumps_params={'ensure_ascii': False})


