from django.conf.urls import url

from DB.base_view import BaseVerifyView
from user.views import LoginView, RegisterView, index, MemberView, ForgetPassView, PersonalCenterView, SendMsm, \
    ResetPasswordView, saftystep, ResetPhoneView, AddressView, AddressAddView, delAddress, AddressEditView

urlpatterns = [
    url(r'^register/$', RegisterView.as_view(), name="用户注册"),
    url(r'^login/$', LoginView.as_view(), name="用户登录"),
    url(r'^index/$', index, name="首页"),
    url(r'^member/$', MemberView.as_view(), name="个人中心"),
    url(r'^PersonalCenter/$', PersonalCenterView.as_view(), name="个人资料"),
    url(r'^forgetpassword/$', ForgetPassView.as_view(), name="忘记密码"),
    # url(r'^code/$', user_code, name="验证码"),
    url(r'^SendMsm/$', SendMsm.as_view(), name="验证码"),
    url(r'^resetpassword/$', ResetPasswordView.as_view(), name="重置密码"),
    url(r"^saftystep/$", saftystep, name='安全设置页'),
    url(r"^resetphone/$", ResetPhoneView.as_view(), name='重置手机号码'),
    url(r'^address/$', AddressView.as_view(), name="收货地址首页"),  # 收货地址首页
    url(r'^address/add/$', AddressAddView.as_view(), name="收货地址添加"),  # 收货地址添加
    url(r'^address/edit/(?P<id>\d+)/$', AddressEditView.as_view(), name="收货地址编辑"),  # 收货地址编辑
    url(r'^address/del/$', delAddress, name="收货地址删除"),  # 收货地址删除



]
