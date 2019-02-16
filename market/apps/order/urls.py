from django.conf.urls import url

from order.views import ConfirmOrder, ShowOrder, Pay

urlpatterns = [
    url(r'^confirm/$', ConfirmOrder.as_view(), name="确认订单"),
    url(r'^show/$', ShowOrder.as_view(), name="确认支付"),
    url(r'^pay/$', Pay.as_view(), name='支付结果'),
]
