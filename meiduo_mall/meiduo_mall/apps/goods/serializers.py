from rest_framework.serializers import ModelSerializer
from drf_haystack.serializers import HaystackSerializer
from goods.models import SKU
from goods.search_indexes import SKUIndex

class SKUSerialzier(ModelSerializer):
    class Meta:
        model=SKU
        fields="__all__"

class SKUIndexSerializer(HaystackSerializer):
    object=SKUSerialzier()
    class Meta:
        index_classes=[SKUIndex]
        fields=("text","object")

class SKUSearchSerializers(HaystackSerializer):
    object = SKUSerialzier()
    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'object')
