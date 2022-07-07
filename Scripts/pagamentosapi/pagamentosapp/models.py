from typing import Any
from django.db import models


# Create your models here.
class BaiPaga(models.Model):
    customerMsisdn = models.CharField(max_length=60)
    totalAmount = models.CharField(max_length=60)
    currency = models.CharField(max_length=60)
    apiKey = models.CharField(max_length=60)
    appCode = models.CharField(max_length=60, default = "")
    email = models.CharField(max_length = 80, default = "")
    tokenApp = models.CharField(max_length = 1024, default = "")
    status = models.CharField(max_length=60, default="CREATED")
    reference = models.CharField(max_length=60, unique=True)


class MulticaixaExpress(models.Model):
    reference = models.CharField(max_length=60, unique=True)
    amount = models.CharField(max_length=60)
    currency = models.CharField(max_length=60)
    token = models.CharField(max_length=60)
    terminal = models.CharField(max_length=60, default = "")
    mobile = models.CharField(max_length=60, default = "")
    callbackUrl = models.CharField(max_length=60, default = "")
    card = models.CharField(max_length=60, default = "")
    status = models.CharField(max_length=60, default="CREATED")
    email = models.CharField(max_length = 80, default = "")
    tokenApp = models.CharField(max_length = 1024, default = "")

class References(models.Model):
    reference = models.IntegerField(unique=True)
    user_id= models.IntegerField()
    reference_id = models.IntegerField()
    valueUSD = models.FloatField()



