from django.db.models import fields
from rest_framework import serializers
from .models import BaiPaga, MulticaixaExpress, References

class BaiPagaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaiPaga
        fields = ('customerMsisdn', 'totalAmount', 'currency', 'apiKey', 'appCode', 'tokenApp', 'email', 'status', 'reference')


class MulticaixaExpressSerializer(serializers.ModelSerializer):
    class Meta:
        model = MulticaixaExpress
        fields = ('reference', 'amount', 'currency', 'token', 'terminal', 'mobile', 'callbackUrl', 'card', 'status', 'email', 'tokenApp')

class ReferencesSerializer(serializers.ModelSerializer):
    class Meta:
        model = References
        fields = ('id', 'reference', 'user_id', 'reference_id')
