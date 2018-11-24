from rest_framework import serializers

from .models import Area
from users.models import Address


class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ("id", "name")


class AddressSerializer(serializers.ModelSerializer):
    city_id = serializers.IntegerField(write_only=True)
    district_id = serializers.IntegerField(write_only=True)
    province_id = serializers.IntegerField(write_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)
    province = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Address
        exclude = ("user",)


    def create(self, validated_data):
        user=self.context["request"].user
        # validated_data添加用户数据
        validated_data["user"]=user

        address = super().create(validated_data)


        return address
