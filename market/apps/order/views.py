import random
from datetime import datetime

from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django_redis import get_redis_connection

from DB.base_view import BaseVerifyView
from cart.helper import get_cart_key, json_msg
from goods.models import GoodsSKU

from order.models import Transport, Order, OrderGoods

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

        # >>>1 . 操作订单基本信息表
        order_sn = "{}{}{}".format(datetime.now().strftime("%Y%m%d%H%M%S"), user_id, random.randrange(10000, 99999))
        address_info = "{}{}{}-{}".format(address.hcity, address.hproper, address.harea, address.detail)
        order = Order.objects.create(
            user=user,
            order_sn=order_sn,
            transport_price=transport.price,
            transport=transport.name,
            username=address.username,
            phone=address.phone,
            address=address_info
        )

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
                return JsonResponse(json_msg(5, "商品不存在"))

            # 获取购物车中商品的数量
            # redis 基于内存的存储,有可能数据会丢失
            try:
                count = r.hget(cart_key, sku_id)
                count = int(count)
            except:
                return JsonResponse(json_msg(6, "购物车中数量不存在!"))

            # 判断库存是否足够
            if goods_sku.stock < count:
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
            goods_sku.stock -= count
            goods_sku.sale_num += count
            goods_sku.save()

        # 3. 反过头来操作订单基本信息表 商品总金额 和 订单总金额
        # 订单总金额
        order_price = goods_total_price + transport.price
        order.goods_total_price = goods_total_price
        order.order_price = order_price
        order.save()

        # 4. 清空redis中的购物车数据(对应sku_id)
        r.hdel(cart_key, *sku_ids)

        # 3. 合成响应
        return JsonResponse(json_msg(0, "创建订单成功!", data=order_sn))


class ShowOrder(BaseVerifyView):
    """确认支付页面"""

    def get(self, request):
        # 接收用户id
        user_id = request.session.get("ID")
        # 接收order_sn
        order_sn = request.GET.get("order_sn")

        try:
            order = Order.objects.get(order_sn=order_sn, user_id=user_id)
        except Order.DoesNotExist:
            return redirect("cart:购物车页面")

        # 计算订单总金额
        total = order.order_amount + order.transport_price
        # 渲染订单到页面
        context = {
            "order": order,
            "total": total,
        }
        return render(request, 'order/order.html', context)

    def post(self, request):
        pass
