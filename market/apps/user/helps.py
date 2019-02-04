from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.profile import region_provider
from django.http import JsonResponse
from django.shortcuts import redirect
from aliyunsdkdysmsapi.request.v20170525 import SendSmsRequest

# 将验证登录的方法写成装饰器,在每次进行验证session中的数据
from market.settings import ACCESS_KEY_ID, ACCESS_KEY_SECRET
from cart.helper import json_msg


def check_login(func):
    def verify_login(request, *args, **kwargs):
        # 判断是否登录
        # 根据session里面的id 判断
        if request.session.get('ID') is None:
            # 将上个请求地址保存到session
            referer = request.META.get('HTTP_REFERER', None)
            if referer:
                request.session['referer'] = referer

                # 判断 是否为ajax请求
            if request.is_ajax():
                return JsonResponse(json_msg(1, '未登录'))

            # 跳转到登录
            return redirect('用户:用户登录')
        else:
            # 调用原函数
            return func(request, *args, **kwargs)

    # 返回新函数
    return verify_login


# # 将验证登录的方法写成装饰器,在每次进行验证session中的数据
# def check_login_view(func):
#     def verify_login(request, *args, **kwargs):
#         # 判断是否登录
#         # 根据session里面的id 判断
#         if request.session.get('ID') is None:
#             # 跳转到登录
#             return redirect('用户:用户登录')
#         else:
#             # 调用原函数
#             return func(request, *args, **kwargs)
#
#     # 返回新函数
#     return verify_login


def login(request, user):  # 保存session的方法
    request.session['ID'] = user.pk
    request.session['username'] = user.username
    request.session['use_img'] = user.use_img
    request.session.set_expiry(0)  # 设置session时间,关闭浏览器就消失


# 完成 定义一个方法 发送短信
# 注意：不要更改
REGION = "cn-hangzhou"
PRODUCT_NAME = "Dysmsapi"
DOMAIN = "dysmsapi.aliyuncs.com"

acs_client = AcsClient(ACCESS_KEY_ID, ACCESS_KEY_SECRET, REGION)
region_provider.add_endpoint(PRODUCT_NAME, REGION, DOMAIN)


def send_sms(business_id, phone_numbers, sign_name, template_code, template_param=None):
    smsRequest = SendSmsRequest.SendSmsRequest()
    # 申请的短信模板编码,必填
    smsRequest.set_TemplateCode(template_code)

    # 短信模板变量参数
    if template_param is not None:
        smsRequest.set_TemplateParam(template_param)

    # 设置业务请求流水号，必填。
    smsRequest.set_OutId(business_id)

    # 短信签名
    smsRequest.set_SignName(sign_name)

    # 数据提交方式
    # smsRequest.set_method(MT.POST)

    # 数据提交格式
    # smsRequest.set_accept_format(FT.JSON)

    # 短信发送的号码列表，必填。
    smsRequest.set_PhoneNumbers(phone_numbers)

    # 调用短信发送接口，返回json
    smsResponse = acs_client.do_action_with_exception(smsRequest)

    # TODO 业务处理

    return smsResponse
