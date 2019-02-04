from django.shortcuts import redirect
from django.utils.decorators import method_decorator
from django.views import View

from user.helps import check_login


class BaseVerifyView(View):
    # 基础类视图，用于验证是否登录
    @method_decorator(check_login)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
