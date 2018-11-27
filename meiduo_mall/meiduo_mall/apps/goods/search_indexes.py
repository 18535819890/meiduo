from haystack import indexes

from .models import SKU


class SKUIndex(indexes.SearchIndex, indexes.Indexable):
    """
    SKU索引数据模型类
    """
    #通过创建索引类，来指明让搜索引擎对哪些字段建立索引，也就是可以通过哪些字段的关键字来检索数据。
    text = indexes.CharField(document=True, use_template=True)
    """其中text字段我们声明为document=True，表名该字段是主要进行关键字查询的字段，
    该字段的索引值可以由多个数据库模型类字段组成，
    具体由哪些模型类字段组成，我们用use_template=True表示后续通过模板来指明。"""

    def get_model(self):
        """根据这个模型类建立索引"""
        return SKU

    def index_queryset(self, using=None):
        """返回模型类中要建立索引的数据查询集"""
        return self.get_model().objects.filter(is_launched=True)
        #is_launched=True表示上架的商品