from django.db import models

# Create your models here.
from utils.models import BaseModel


class Area(models.Model):
       name = models.CharField(max_length=20, verbose_name='名称', db_column='Name')
       parent = models.ForeignKey('self', on_delete= models.CASCADE, related_name= '省市', db_column='ParentId')

       class Meta:
              db_table = 'tb_area'
              verbose_name = '省市区数据'
              verbose_name_plural = verbose_name