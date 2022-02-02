from django.db.models import fields
from rest_framework import serializers
from .models import BaiPaga, MulticaixaExpress

class BaiPagaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaiPaga
        fields = ('customerMsisdn', 'totalAmount', 'currency', 'apiKey', 'appCode')


class MulticaixaExpressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MulticaixaExpress
        fields = ('reference', 'amount', 'currency', 'token', 'terminal', 'mobile', 'callbackUrl', 'card')