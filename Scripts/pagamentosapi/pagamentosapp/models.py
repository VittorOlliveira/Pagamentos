from typing import Any
from django.db import models

# Create your models here.
class BaiPaga(models.Model):
    customerMsisdn = models.CharField(max_length=60)
    totalAmount = models.CharField(max_length=60)
    currency = models.CharField(max_length=60)
    apiKey = models.CharField(max_length=60)
    appCode = models.CharField(max_length=60, default="")

class MulticaixaExpress(models.Model):
    reference = models.CharField(max_length=60)
    amount = models.CharField(max_length=60)
    currency = models.CharField(max_length=60)
    token = models.CharField(max_length=60)
    terminal = models.CharField(max_length=60, default="")
    mobile = models.CharField(max_length=60, default="")
    callbackUrl = models.CharField(max_length=60, default="")
    card = models.CharField(max_length=60, default="")
