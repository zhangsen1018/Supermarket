from haystack import indexes
from goods.models import GoodsSKU


class GoodsSKUIndex(indexes.SearchIndex, indexes.Indexable):
    # 用于指定主要索引字段的, 索引字段在模板中指定
    text = indexes.CharField(document=True, use_template=True)

    # 返回模型类
    def get_model(self):
        return GoodsSKU

    # 设置查询集
    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.filter(is_delete=False)
