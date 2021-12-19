from rest_framework import serializers

from .models import Item, Category, SubCategory


class SubCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCategory
        fields = (
            'pk',
            'name', 
            'code',
            'category',
        )

class CategorySerializer(serializers.ModelSerializer):
    sub_category = SubCategorySerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = (
            'pk',
            'name', 
            'code',
            'kind',
            'color',
            'sub_category'
        )

class ItemSubCategorySerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = SubCategory
        fields = (
            'pk',
            'name', 
            'code',
            'category',
        )

class ItemSerializer(serializers.ModelSerializer):
    sub_category = ItemSubCategorySerializer(read_only=True)
    sub_category_id = serializers.PrimaryKeyRelatedField(queryset=SubCategory.objects.all(), write_only=True)

    class Meta:
        model = Item
        fields = (
            'pk',
            'name',
            'amount_income',
            'amount_expenses',
            'sub_category',
            'sub_category_id',
        )
    
    def create(self, validated_data):
        validated_data['sub_category'] = validated_data.get('sub_category_id', None)
        
        if validated_data['sub_category'] is None:
            raise serializers.ValidationError("sub_cateory not found.")

        del validated_data['sub_category_id']
        
        return Item.objects.create(**validated_data)
