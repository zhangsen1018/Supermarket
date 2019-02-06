from django.contrib import admin

# Register your models here.

from goods.models import Activity, Banner, GoodsSKU, GoodsSPU, Unit, Category, Gallery, ActivityZoneGoods, ActivityZone


# 首页活动表
@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_per_page = 4  #: 每页显示条数

    actions_on_top: True  # 操作是否在上面显示, 默认  True  ,反正两个相反
    actions_on_bottom: True  # 操作是否在下面显示, 默认   False

    # 自定义显示列，在models类中对字段有方法的就填方法名
    list_display = ['id', 'title', 'img_url', 'url_site']

    # 设置在列表页字段上添加一个 a标签, 从而进入到编辑页面,在models类中对字段有方法的就填方法名
    list_display_links = ['id', 'title', 'img_url', 'url_site']

    # 列表右侧栏过滤器,只能写一个
    list_filter = ['title']

    # 搜索框,搜索字段 也只能写一个
    search_fields = ['title']

    # fields = []: 定义在添加或者编辑的时候操作哪些字段，一般不设

    # 对可编辑区域分组,列表里面的字段填写模型的属性，
    fieldsets = (
        ('活动名称', {"fields": ['title']}),
        ('活动图片地址', {"fields": ['img_url']}),
        ('活动的url地址', {"fields": ['url_site']}),
    )


# 首页轮播商品表
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_per_page = 4  #: 每页显示条数

    actions_on_top: True  # 操作是否在上面显示, 默认  True  ,反正两个相反
    actions_on_bottom: True  # 操作是否在下面显示, 默认   False

    # 自定义显示列，在models类中对字段有方法的就填方法名
    list_display = ['id', 'name', 'goods_sku', 'img_url', 'order', 'Create_time', 'update_time',
                    'is_delete']

    # 设置在列表页字段上添加一个 a标签, 从而进入到编辑页面,在models类中对字段有方法的就填方法名
    list_display_links = ['id', 'name', 'goods_sku', 'img_url', 'order', 'Create_time', 'update_time',
                          'is_delete']

    # 列表右侧栏过滤器,只能写一个
    list_filter = ['name']

    # 搜索框,搜索字段 也只能写一个
    search_fields = ['name']

    # fields = []: 定义在添加或者编辑的时候操作哪些字段，一般不设

    # 对可编辑区域分组,列表里面的字段填写模型的属性，
    fieldsets = (
        ('轮播活动名', {"fields": ['name']}),
        ('商品SKU', {"fields": ['goods_sku']}),
        ('轮播图片地址', {"fields": ['img_url']}),
        ('排序', {"fields": ['order']}),
    )


# 商品sku
class GalleryInline(admin.TabularInline):
    model = Gallery
    extra = 2


# 商品SKU表
@admin.register(GoodsSKU)
class GoodsSKUAdmin(admin.ModelAdmin):
    list_per_page = 4  #: 每页显示条数

    actions_on_top: True  # 操作是否在上面显示, 默认  True  ,反正两个相反
    actions_on_bottom: True  # 操作是否在下面显示, 默认   False

    # 自定义显示列，在models类中对字段有方法的就填方法名
    list_display = ['id', 'sku_name', 'brief', 'price', 'unit', 'stock', 'sale_num', 'logo',
                    'is_on_sale', 'category', 'goods_spu', 'Create_time', 'update_time', 'is_delete']

    # 在列表可以编辑上下架
    list_editable = ['is_on_sale']

    # 设置在列表页字段上添加一个 a标签, 从而进入到编辑页面,在models类中对字段有方法的就填方法名
    list_display_links = ['id', 'sku_name', 'brief', 'price', 'unit', 'stock', 'sale_num', 'logo',
                          'category', 'goods_spu', 'Create_time', 'update_time', 'is_delete']

    # 列表右侧栏过滤器,只能写一个
    list_filter = ['sku_name']

    # 搜索框,搜索字段 也只能写一个
    search_fields = ['sku_name']

    # fields = []: 定义在添加或者编辑的时候操作哪些字段，一般不设

    # 对可编辑区域分组,列表里面的字段填写模型的属性，
    fieldsets = (
        ('商品SKU名称', {"fields": ['sku_name']}),
        ('商品简介', {"fields": ['brief']}),
        ('价格', {"fields": ['price']}),
        ('单位', {"fields": ['unit']}),
        ('库存', {"fields": ['stock']}),
        ('销量', {"fields": ['sale_num']}),
        ('商品logo', {"fields": ['logo']}),
        ('是否上架', {"fields": ['is_on_sale']}),
        ('商品分类', {"fields": ['category']}),
        ('商品SPU', {"fields": ['goods_spu']}),
    )
    # 关联模型
    inlines = [
        GalleryInline,
    ]


# 商品SPU表
@admin.register(GoodsSPU)
class GoodsSPUAdmin(admin.ModelAdmin):
    list_per_page = 4  #: 每页显示条数

    actions_on_top: True  # 操作是否在上面显示, 默认  True  ,反正两个相反
    actions_on_bottom: True  # 操作是否在下面显示, 默认   False

    # 自定义显示列，在models类中对字段有方法的就填方法名
    list_display = ['id', 'spu_name', 'content']

    # 设置在列表页字段上添加一个 a标签, 从而进入到编辑页面,在models类中对字段有方法的就填方法名
    list_display_links = ['id', 'spu_name', 'content']

    # 列表右侧栏过滤器,只能写一个
    list_filter = ['spu_name']

    # 搜索框,搜索字段 也只能写一个
    search_fields = ['spu_name']

    # fields = []: 定义在添加或者编辑的时候操作哪些字段，一般不设

    # 对可编辑区域分组,列表里面的字段填写模型的属性，
    fieldsets = (
        ('商品SPU名称', {"fields": ['spu_name']}),
        ('商品spu详情', {"fields": ['content']}),
    )


# 商品单位表
@admin.register(Unit)
class UnitAdmin(admin.ModelAdmin):
    list_per_page = 4  #: 每页显示条数

    actions_on_top: True  # 操作是否在上面显示, 默认  True  ,反正两个相反
    actions_on_bottom: True  # 操作是否在下面显示, 默认   False

    # 自定义显示列，在models类中对字段有方法的就填方法名
    list_display = ['id', 'name', 'Create_time', 'update_time', 'is_delete']

    # 设置在列表页字段上添加一个 a标签, 从而进入到编辑页面,在models类中对字段有方法的就填方法名
    list_display_links = ['id', 'name', 'Create_time', 'update_time', 'is_delete']

    # 列表右侧栏过滤器,只能写一个
    list_filter = ['name']

    # 搜索框,搜索字段 也只能写一个
    search_fields = ['name']


# 商品分类表
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_per_page = 4  #: 每页显示条数

    actions_on_top: True  # 操作是否在上面显示, 默认  True  ,反正两个相反
    actions_on_bottom: True  # 操作是否在下面显示, 默认   False

    # 自定义显示列，在models类中对字段有方法的就填方法名
    list_display = ['id', 'cate_name', 'brief', 'order', 'Create_time', 'update_time', 'is_delete']

    # 设置在列表页字段上添加一个 a标签, 从而进入到编辑页面,在models类中对字段有方法的就填方法名
    list_display_links = ['id', 'cate_name', 'brief', 'order', 'Create_time', 'update_time', 'is_delete']

    # 列表右侧栏过滤器,只能写一个
    list_filter = ['cate_name']

    # 搜索框,搜索字段 也只能写一个
    search_fields = ['cate_name']

    # fields = []: 定义在添加或者编辑的时候操作哪些字段，一般不设

    # 对可编辑区域分组,列表里面的字段填写模型的属性，
    fieldsets = (
        ('分类名称', {"fields": ['cate_name']}),
        ('描述', {"fields": ['brief']}),
        ('排序', {"fields": ['order']}),
    )


class ActivityZoneGoodsInline(admin.TabularInline):
    model = ActivityZoneGoods
    extra = 2


@admin.register(ActivityZone)
class ActivityZoneAdmin(admin.ModelAdmin):
    inlines = [
        ActivityZoneGoodsInline

    ]
