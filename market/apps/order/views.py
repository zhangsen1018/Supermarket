import os
import random
from datetime import datetime
from time import sleep

from alipay import AliPay
from django.db import transaction
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views import View
from django_redis import get_redis_connection

from DB.base_view import BaseVerifyView
from cart.helper import get_cart_key, json_msg
from goods.models import GoodsSKU
from market import settings

from order.models import Transport, Order, OrderGoods, Payment

from user.models import Users, SpAddress


class ConfirmOrder(BaseVerifyView):
    """确认订单页面"""

    def get(self, request):
        """
            1. 如果没有收货地址显示添加收货地址
               如果有收货地址, 显示默认收货地址, 如果没有默认显示第一个


            2. 展示商品信息
                a. 获取商品sku_ids
                    如何获取多个参数的值 getlist() get()只能获取一个

                b. 根据商品id获取商品信息 并且 获取购物车redis中的数量


        """
        user_id = request.session.get("ID")
        # >>>> 1. 收货地址处理
        address = SpAddress.objects.filter(user_id=user_id).order_by("-isDefault").first()
        # address = None

        # 处理商品信息
        sku_ids = request.GET.getlist("sku_ids")
        # 准备空列表 装商品
        goods_skus = []
        # 准备商品总计
        goods_total_price = 0

        # 准备redis
        r = get_redis_connection()
        # 准备键
        cart_key = get_cart_key(user_id)

        # 遍历
        for sku_id in sku_ids:
            # 商品信息
            try:
                goods_sku = GoodsSKU.objects.get(pk=sku_id)
            except GoodsSKU.DoesNotExist:
                # 商品不存在就回到购物车
                return redirect("cart:购物车展示")

            # 获取对应商品的数量
            try:
                count = r.hget(cart_key, sku_id)
                count = int(count)
            except:
                # 商品不存在就回到购物车
                return redirect("cart:购物车展示")

            # 保存到商品对象上
            goods_sku.count = count

            # 装商品
            goods_skus.append(goods_sku)

            # 统计商品总计
            goods_total_price += goods_sku.price * count

        # 获取运输方式
        transports = Transport.objects.filter(is_delete=False).order_by('price')

        # 渲染数据
        context = {
            'address': address,
            'goods_skus': goods_skus,
            'goods_total_price': goods_total_price,
            'transports': transports,
        }
        return render(request, 'order/tureorder.html', context=context)

    @transaction.atomic
    def post(self, request):
        """
            保存订单数据
            1. 订单基本信息表 和 订单商品表
        """
        # 1. 接收参数
        transport_id = request.POST.get('transport')
        sku_ids = request.POST.getlist('sku_ids')
        address_id = request.POST.get('address')

        # 接收用户的id
        user_id = request.session.get("ID")
        user = Users.objects.get(pk=user_id)

        # 验证数据的合法性
        try:
            transport_id = int(transport_id)
            address_id = int(address_id)
            sku_ids = [int(i) for i in sku_ids]
        except:
            return JsonResponse(json_msg(2, "参数错误"))

        # 验证收货地址和运输方式存在
        try:
            address = SpAddress.objects.get(pk=address_id)
        except SpAddress.DoesNotExist:
            return JsonResponse(json_msg(3, "收货地址不存在!"))

        try:
            transport = Transport.objects.get(pk=transport_id)
        except Transport.DoesNotExist:
            return JsonResponse(json_msg(4, "运输方式不存在!"))

        # 2. 操作数据
        # 创建保存点
        sid = transaction.savepoint()
        # >>>1 . 操作订单基本信息表
        order_sn = "{}{}{}".format(datetime.now().strftime("%Y%m%d%H%M%S"), user_id, random.randrange(10000, 99999))
        address_info = "{}{}{}-{}".format(address.hcity, address.hproper, address.harea, address.detail)
        try:
            order = Order.objects.create(
                user=user,
                order_sn=order_sn,
                transport_price=transport.price,
                transport=transport.name,
                username=address.username,
                phone=address.phone,
                address=address_info
            )
        except:
            return JsonResponse(json_msg(8, "创建订单基本数据失败"))

        # >>>2. 操作订单商品表
        # 操作redis
        r = get_redis_connection()
        cart_key = get_cart_key(user_id)

        # 准备个变量保存商品总金额
        goods_total_price = 0
        for sku_id in sku_ids:

            # 获取商品对象
            try:
                goods_sku = GoodsSKU.objects.get(pk=sku_id, is_delete=False, is_on_sale=True)
            except GoodsSKU.DoesNotExist:
                # 回滚数据
                transaction.savepoint_rollback(sid)
                return JsonResponse(json_msg(5, "商品不存在"))

            # 获取购物车中商品的数量
            # redis 基于内存的存储,有可能数据会丢失
            try:
                count = r.hget(cart_key, sku_id)
                count = int(count)
            except:
                transaction.savepoint_rollback(sid)
                return JsonResponse(json_msg(6, "购物车中数量不存在!"))

            # 判断库存是否足够
            if goods_sku.stock < count:
                transaction.savepoint_rollback(sid)
                return JsonResponse(json_msg(7, "库存不足!"))

            # 保存订单商品表
            order_goods = OrderGoods.objects.create(
                order=order,
                goods_sku=goods_sku,
                price=goods_sku.price,
                count=count
            )

            # 添加商品总金额
            goods_total_price += goods_sku.price * count

            # 扣除库存, 销量增加
            # rs = GoodsSKU.objects.filter(pk=sku_id,stock=goods_sku.stock).update(stock=goods_sku.stock-count)
            goods_sku.stock -= count
            goods_sku.sale_num += count
            goods_sku.save()

        # 3. 反过头来操作订单基本信息表 商品总金额 和 订单总金额
        # 订单总金额
        try:
            order_price = goods_total_price + transport.price
            order.goods_total_price = goods_total_price
            order.order_price = order_price
            order.save()
        except:
            # 回滚
            transaction.savepoint_rollback(sid)
            return JsonResponse(json_msg(9, "更新订单失败"))
        # transaction.savepoint_rollback(sid)
        # 4. 清空redis中的购物车数据(对应sku_id)
        r.hdel(cart_key, *sku_ids)

        # 下单成功, 提交事务
        transaction.savepoint_commit(sid)

        # 3. 合成响应
        return JsonResponse(json_msg(0, "创建订单成功!", data=order_sn))


class ShowOrder(BaseVerifyView):
    """确认支付页面"""

    def get(self, request):
        # 接收参数
        order_sn = request.GET.get('order_sn')
        user_id = request.session.get("ID")
        # 操作数据
        # 获取订单信息
        order = Order.objects.get(order_sn=order_sn, user_id=user_id)

        # 获取支付方式
        payments = Payment.objects.filter(is_delete=False).order_by('id')

        # 渲染数据
        context = {
            'order': order,
            'payments': payments,
        }

        return render(request, 'order/order.html', context=context)

    def post(self, request):

        # 参数接收
        payment = request.POST.get('payment')
        order_sn = request.POST.get('order_sn')
        user_id = request.session.get('ID')

        # 判断参数合法性
        try:
            payment = int(payment)
        except:
            return JsonResponse(json_msg(1, "参数错误"))

        # 支付方式存在
        try:
            payment = Payment.objects.get(pk=payment)
        except Payment.DoesNotExist:
            return JsonResponse(json_msg(2, "支付方式不存在"))

        # 判断该订单是否是自己的, 并且是一个未支付的订单
        try:
            order = Order.objects.get(user_id=user_id, order_sn=order_sn, order_status=0)
        except Order.DoesNotExist:
            return JsonResponse(json_msg(3, "订单不满足要求"))

        # 判断 用户是否需要使用支付宝支付
        if payment.name == "支付宝":
            # 构造支付请求
            app_private_key_string = open(os.path.join(settings.BASE_DIR, "alipay/user_private_key.txt")).read()
            alipay_public_key_string = open(os.path.join(settings.BASE_DIR, 'alipay/alipay_public_key.txt')).read()

            # 初始化对象
            alipay = AliPay(
                appid="2016092400582019",
                app_notify_url=None,  # 默认回调url
                app_private_key_string=app_private_key_string,
                # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
                alipay_public_key_string=alipay_public_key_string,
                sign_type="RSA2",  # RSA 或者 RSA2
                debug=True  # 默认False
            )

            # 构造请求地址
            order_string = alipay.api_alipay_trade_wap_pay(
                out_trade_no=order.order_sn,  # 订单编号
                total_amount=str(order.order_price),  # 订单金额
                subject="张爸爸超市订单支付",  # 订单描述
                return_url="http://127.0.0.1:8008/order/pay/",  # 同步通知地址
                notify_url=None  # 异步通知地址 重要
            )

            # 拼接地址
            url = "https://openapi.alipaydev.com/gateway.do?" + order_string

            # 通过json返回请求地址
            return JsonResponse(json_msg(0, "创建支付地址成功", data=url))
        else:
            return JsonResponse(json_msg(4, "该支付方式暂不支支持"))


class Pay(BaseVerifyView):
    """展示支付结果"""

    def get(self, request):

        # 查询订单是否交易成功
        # 构造支付请求
        app_private_key_string = open(os.path.join(settings.BASE_DIR, "alipay/user_private_key.txt")).read()
        alipay_public_key_string = open(os.path.join(settings.BASE_DIR, 'alipay/alipay_public_key.txt')).read()

        # 初始化对象
        alipay = AliPay(
            appid="2016092400582019",
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False
        )

        # 获取订单编号
        order_sn = request.GET.get('out_trade_no')
        total_amount = request.GET.get('total_amount')

        # check order status
        paid = False
        for i in range(10):
            # 根据订单编号查询
            result = alipay.api_alipay_trade_query(out_trade_no=order_sn)
            print(result)
            if result.get("trade_status", "") == "TRADE_SUCCESS":
                # 支付成功
                paid = True
                break

            # 继续执行
            # check every 3s, and 10 times in all
            sleep(3)
            print("not paid...")

        # 判断支付是否成功
        context = {
            'order_sn': order_sn,
            'total_amount': total_amount,
        }
        if paid is False:
            # 支付失败
            context['result'] = "支付失败"
        else:
            # 支付成功
            context['result'] = "支付成功"

        return render(request, "order/pay.html", context=context)


class Notify(View):
    def post(self, request):
        # 查询订单是否交易成功
        # 构造支付请求
        app_private_key_string = open(os.path.join(settings.BASE_DIR, "alipay/user_private_key.txt")).read()
        alipay_public_key_string = open(os.path.join(settings.BASE_DIR, 'alipay/alipay_public_key.txt')).read()

        # 初始化对象
        alipay = AliPay(
            appid="2016092400582019",
            app_notify_url=None,  # 默认回调url
            app_private_key_string=app_private_key_string,
            # 支付宝的公钥，验证支付宝回传消息使用，不是你自己的公钥,
            alipay_public_key_string=alipay_public_key_string,
            sign_type="RSA2",  # RSA 或者 RSA2
            debug=True  # 默认False
        )

        # 获取订单编号
        order_sn = request.POST.get('out_trade_no')
        order = Order.objects.get(order_sn=order_sn)
        # check order status
        paid = False
        for i in range(10):
            # 根据订单编号查询
            result = alipay.api_alipay_trade_query(out_trade_no=order_sn)
            print(result)
            if result.get("trade_status", "") == "TRADE_SUCCESS":
                # 支付成功
                paid = True
                break

            # 继续执行
            # check every 3s, and 10 times in all
            sleep(3)
            print("not paid...")

        # 判断支付是否成功
        # 修改订单状态
        if paid is True:
            # 支付成功
            order.order_status = 1
            order.save()

        return HttpResponse("success")
