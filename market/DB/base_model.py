# 所有模型用到的基类
from django.db import models


class Base_model(models.Model):
    is_delete = models.BooleanField(default=False)  # 假删除
    Create_time = models.DateField(auto_now_add=True)  # 添加时间
    update_time = models.DateField(auto_now=True)  # 修改时间

    class Meta:
        abstract = True  # 说明这个对象是抽象的,不会迁移
