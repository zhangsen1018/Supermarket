from django.conf.urls import url

from cart.views import AddCartView, ShopCartView

urlpatterns = [
    url(r'^add/$', AddCartView.as_view(), name="添加购物车"),
    url(r'^$', ShopCartView.as_view(), name="购物车页面"),
]
