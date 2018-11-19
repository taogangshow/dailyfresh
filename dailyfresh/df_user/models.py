# -*- coding:utf-8 -*-
from django.db import models

class UserInfo(models.Model):
    uname = models.CharField(max_length=20)
    upwd = models.CharField(max_length=40)
    uemail = models.CharField(max_length=30)
    # 填写默认值后，不需要做迁移，因为默认值不会影响数据库表结构
    # 如果将后面的default=''改为null = True则就需要做迁移
    # default,blank都是python层面的约束,不影响数据库表结构
    ushou = models.CharField(max_length=20,default='')
    uaddress = models.CharField(max_length=100,default='')
    uyoubian = models.CharField(max_length=6,default='')
    uphone = models.CharField(max_length=11,default='')
