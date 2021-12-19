from items.models import Item
from wallets.models import Wallet
from rest_framework import serializers

from .models import Supplier, Transaction
from wallets.serializers import WalletSerializer
from items.serializers import ItemSerializer


class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = (
            'pk',
            'name',
        )


class TransactionSerializer(serializers.ModelSerializer):
    items = ItemSerializer(many=True)
    supplier = SupplierSerializer(read_only=True)
    supplier_id = serializers.PrimaryKeyRelatedField(queryset=Supplier.objects.all(), write_only=True)
    wallet_income = WalletSerializer(read_only=True)
    wallet_income_id = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all(), write_only=True)
    wallet_expenses = WalletSerializer(read_only=True)
    wallet_expenses_id = serializers.PrimaryKeyRelatedField(queryset=Wallet.objects.all(), write_only=True)


    def transaction_validated_data_id_to_pk(self, validated_data):
        validated_data['supplier'] = validated_data.get('supplier_id', None)
        validated_data['wallet_income'] = validated_data.get('wallet_income_id', None)
        validated_data['wallet_expenses'] = validated_data.get('wallet_expenses_id', None)

        if validated_data['supplier'] is None:
            raise serializers.ValidationError("supplier not found.") 
        
        if validated_data['wallet_income'] is None:
            raise serializers.ValidationError("wallet not found.")
        
        if validated_data['wallet_expenses'] is None:
            raise serializers.ValidationError("wallet not found.") 

        del validated_data['supplier_id']
        del validated_data['wallet_income_id']
        del validated_data['wallet_expenses_id']

        return validated_data
    
    def item_transaction_validated_data_id_to_pk(self, item):
        item['sub_category'] = item.get('sub_category_id', None)
        
        if item['sub_category'] is None:
            raise serializers.ValidationError("sub_cateory not found.")

        del item['sub_category_id']

        return item

    

    def create(self, validated_data):
        validated_data = self.transaction_validated_data_id_to_pk(validated_data)

        # POSTされたアイテムを分離
        items_data = validated_data.pop('items')
        # トランザクションを作成
        transaction = Transaction.objects.create(**validated_data)
        # トランザクションを外部キー指定でアイテムを作成
        for item_data in items_data:
            item_data = self.item_transaction_validated_data_id_to_pk(item_data)
            
            Item.objects.create(transaction=transaction, **item_data)
        return transaction
    
    def update(self, instance, validated_data):
        validated_data = self.transaction_validated_data_id_to_pk(validated_data)

        items = validated_data.pop('items', [])

        Item.objects.filter(transaction=instance.pk).all().delete()

        for item in items:
            item = self.item_transaction_validated_data_id_to_pk(item)
            item['transaction_id'] = instance.pk
            Item.objects.update_or_create(pk=item.get('pk'), defaults=item)
        
        instance.supplier = validated_data['supplier']
        instance.wallet_income = validated_data['wallet_income']
        instance.wallet_expenses = validated_data['wallet_expenses']
        instance.kind = validated_data['kind']
        instance.date = validated_data['date']
        
        instance.save()
        return instance

    class Meta:
        model = Transaction
        fields = (
            'pk',
            'kind',
            'supplier',
            'supplier_id',
            'date',
            'wallet_expenses',
            'wallet_expenses_id',
            'wallet_income',
            'wallet_income_id',
            'items',
        )
