from django.db import models

# Create your models here.

from ckeditor_uploader.fields import RichTextUploadingField
from django.core.validators import MinLengthValidator
from django.db import models

# Create your models here.
from DB.base_model import Base_model

is_on_sale_choices = (
    (False, "下架"),
    (True, "上架"),
)


# 商品模型一：
# 商品分类表
# ID
# 分类名
# 分类简介
# 继承基础Base_model模型
class Category(Base_model):
    cate_name = models.CharField(max_length=50,
                                 validators=
                                 [MinLengthValidator(2)],
                                 verbose_name='分类名称')
    brief = models.CharField(max_length=200,
                             null=True,
                             blank=True,
                             verbose_name='描述')
    order = models.SmallIntegerField(default=0, verbose_name="排序")

    def __str__(self):
        return self.cate_name

    class Meta:
        db_table = 'Category'
        verbose_name = '商品分类表'  # 备注：此模型在后台django中admin管理名字为：商品总表
        verbose_name_plural = verbose_name  # 复数名


# 商品模型二:
# 商品SPU表
# ID
# 名称
# 详情
# 继承基础Base_model模型
class GoodsSPU(Base_model):
    spu_name = models.CharField(max_length=50,
                                validators=[MinLengthValidator(2)],
                                verbose_name='商品SPU名称')
    # 使用ckeditor为我们提供的字段，不用重新迁移就可以
    content = RichTextUploadingField(
        validators=[MinLengthValidator(2)],
        verbose_name='商品spu详情')

    def __str__(self):
        return self.spu_name

    class Meta:
        db_table = 'GoodsSPU'
        verbose_name = '商品SPU表'  # 备注：此模型在后台django中admin管理名字为：商品总表
        verbose_name_plural = verbose_name  # 复数名


# 商品模型三：
# 商品 SKU 单位表
# ID
# 单位名（斤，箱）
# 继承基础Base_model模型
class Unit(Base_model):
    name = models.CharField(max_length=10,
                            verbose_name='单位名')

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'Unit'
        verbose_name = '商品单位表'  # 备注：此模型在后台django中admin管理名字为：商品总表
        verbose_name_plural = verbose_name  # 复数名


# 商品模型四：
# 商品SKU表
# ID
# 商品名
# 简介
# 价格
# 单位    UnitModel
# 库存
# 销量
# LOGO地址
# 是否上架
# 商品分类ID    GoodsClassModel
# 商品spu_id     GoodsSPUModel
# 继承基础Base_model模型
class GoodsSKU(Base_model):
    # 商品名
    sku_name = models.CharField(max_length=100,
                                validators=
                                [MinLengthValidator(2)],
                                verbose_name='商品SKU名称')
    # 简介
    brief = models.CharField(max_length=200,
                             null=True,
                             blank=True,
                             verbose_name='商品简介')
    # 价格（最高金额为10万，小数最多4个小数点）
    price = models.DecimalField(max_digits=10,
                                decimal_places=4,
                                verbose_name='价格')
    # 单位 外键
    unit = models.ForeignKey(to='Unit', verbose_name='单位')

    # 库存
    stock = models.IntegerField(verbose_name='库存',
                                default=0
                                )
    # 销量
    sale_num = models.IntegerField(verbose_name='销量',
                                   default=0
                                   )
    # LOGO地址
    # 默认相册中的第一张图片作为封面图片
    logo = models.ImageField(upload_to='goods/%y%m/%d',
                             verbose_name='商品logo')
    # # 是否上架
    # choic = (
    #     (0, '未上架'),
    #     (1, '已上架'),
    # )
    is_on_sale = models.BooleanField(verbose_name="是否上架",
                                     choices=is_on_sale_choices,
                                     default=False)
    # 商品分类ID  外键  Category
    category = models.ForeignKey(to='Category',
                                 verbose_name='商品分类')
    # 商品spu_id   外键  GoodsSPU
    goods_spu = models.ForeignKey(to='GoodsSPU', verbose_name='商品SPU')

    def __str__(self):
        return self.sku_name

    class Meta:
        db_table = 'GoodsSKU'
        verbose_name = '商品SKU表'  # 备注：此模型在后台django中admin管理名字为：商品总表
        verbose_name_plural = verbose_name  # 复数名


# 商品模型五：
# 商品相册表
# ID
# 图片地址
# 商品SKUID    GoodsSKU
# 继承基础Base_model模型
class Gallery(Base_model):
    img_url = models.ImageField(upload_to='goods/%y%m/%d',
                                verbose_name='相册图片地址')
    goods_sku = models.ForeignKey(to='GoodsSKU',
                                  verbose_name='商品SKU')

    class Meta:
        db_table = 'Gallery'
        verbose_name = '商品相册表'  # 备注：此模型在后台django中admin管理名字为：商品总表
        verbose_name_plural = verbose_name  # 复数名

    def __str__(self):
        return "商品相册:{}".format(self.img_url.name)


# 商品首页轮播商品表
# ID
# 名称
# 商品SKUID
# 图片地址
# 排序（order）
# 继承基础Base_model模型
class Banner(Base_model):
    # 名称
    name = models.CharField(verbose_name="轮播活动名",
                            max_length=150,
                            )
    # 商品SKUID     外键
    goods_sku = models.ForeignKey(to='GoodsSKU',
                                  verbose_name='商品SKU')
    # 图片地址
    img_url = models.ImageField(upload_to='banner/%y%m/%d',
                                verbose_name='轮播图片地址')
    # 排序（order）
    order = models.SmallIntegerField(verbose_name="排序",
                                     default=0,
                                     )

    class Meta:
        db_table = 'Banner'
        verbose_name = '首页轮播商品表'  # 备注：此模型在后台django中admin管理名字为：商品总表
        verbose_name_plural = verbose_name  # 复数名

    def __str__(self):
        return self.name


# 商品首页活动表
# ID
# 名称
# 图片地址
# url地址
# 继承基础Base_model模型
class Activity(Base_model):
    # 名称
    title = models.CharField(max_length=150,
                             verbose_name='活动名称'
                             )
    # 图片地址
    img_url = models.ImageField(upload_to='activity/%y%m/%d',
                                verbose_name='活动图片地址')
    # url地址
    url_site = models.URLField(verbose_name='活动的url地址', max_length=200)

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'Activity'
        verbose_name = '首页活动管理'  # 备注：此模型在后台django中admin管理名字为：商品总表
        verbose_name_plural = verbose_name  # 复数名


# 首页活动专区
# ID
# 名称
# 描述
# 排序
# 是否上架
# 继承基础Base_model模型
class ActivityZone(Base_model):
    # 名称
    title = models.CharField(verbose_name='活动专区名称', max_length=150)
    brief = models.CharField(verbose_name="活动专区的简介",
                             max_length=200,
                             null=True,
                             blank=True,
                             )
    order = models.SmallIntegerField(verbose_name="排序",
                                     default=0,
                                     )
    is_on_sale = models.BooleanField(verbose_name="上否上线",
                                     choices=is_on_sale_choices,
                                     default=0,
                                     )
    goods_sku = models.ManyToManyField(to="GoodsSKU", verbose_name="商品")

    def __str__(self):
        return self.title

    class Meta:
        db_table = 'ActivityZone'
        verbose_name = "活动专区管理"
        verbose_name_plural = verbose_name


class ActivityZoneGoods(Base_model):
    # 首页活动专区商品列表

    zone = models.ForeignKey(to="ActivityZone", verbose_name="活动专区")
    goods_sku = models.ForeignKey(to="GoodsSKU", verbose_name="商品SKU")

    class Meta:
        db_table = 'ActivityZoneGoods'
        verbose_name = "首页活动专区商品列表"
        verbose_name_plural = verbose_name
