from rest_framework import serializers

from .models import Wallet


class WalletSerializer(serializers.ModelSerializer):
    amount_sum = serializers.SerializerMethodField()

    class Meta:
        model = Wallet
        fields = (
            'pk',
            'name',
            'color',
            'amount',
            'amount_sum',
            'code',
            'kind',
            'is_favorite',
            'is_hide',
        )

    def get_amount_sum(self, obj):
        income = 0
        expenses = 0

        # POSTした内容を返すときはcontextがNoneになるらしい
        if not set(self.context) >= {'income', 'expenses'}:
            return 0
 
        for i in self.context.get('income'):
            if i['transaction__wallet_income'] == obj.pk:
                income = i['amount']
        for i in self.context.get('expenses'):
            if i['transaction__wallet_expenses'] == obj.pk:
                expenses = i['amount']

        return income - expenses