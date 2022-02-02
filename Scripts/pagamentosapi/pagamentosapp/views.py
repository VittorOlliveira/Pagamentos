from django.shortcuts import render
from requests.api import request
#from requests.models import Response
from rest_framework.response import Response

from rest_framework import viewsets
from rest_framework.views import APIView
from .serializers import BaiPagaSerializer, MulticaixaExpressSerializer
from .models import BaiPaga, MulticaixaExpress
import requests
import json
from rest_framework.decorators import action, api_view
from django.views.decorators.csrf import csrf_exempt
from requests.structures import CaseInsensitiveDict

# Create your views here.
@api_view(['GET', 'POST'])
def BaiPagaViewSet(request):
    
    if request.method == 'POST':

        url = "https://ib.bancobai.ao/QUAMDW-3G/mp-merchant-boapi/api/soap/partners/MobilePaymentsMerchantAcceptancePointSoapApi?wsdl"
        headers = CaseInsensitiveDict()
        print('Hello, BAI PAga')
        headers["Content-Type"] = "application/soap+xml"
        data = """
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:com="com.inm.mobilepayments">
            <soapenv:Header/>
            <soapenv:Body>
                <com:initiateMobilePaymentViaOtpRequestFromMerchant>
                    <customerMsisdn>{customerMsisdn}</customerMsisdn>
                    <totalAmount>{totalAmount}</totalAmount>
                    <currency>{currency}</currency>
                    <shoppingCart>
                        <!--Zero or more repetitions:-->
                        <items>
                            <!--Optional:-->
                            <amountPerItem>{amountPerItem}</amountPerItem>
                            <!--Optional:-->
                            <count>1</count>
                            <!--Optional:-->
                            <description>{description}</description>
                            <!--Optional:-->
                            <discount>{discount}</discount>
                            <!--Optional:-->
                            <totalAmount>{totalAmount}</totalAmount>
                        </items>
                    </shoppingCart>
                    <!--Optional:-->
                    <externalReference>2021/002</externalReference>
                    <!--Optional:-->
                    <description>{description}</description>
                    <!--Optional:-->
                    <apiKey>{apiKey}</apiKey>
                </com:initiateMobilePaymentViaOtpRequestFromMerchant>
            </soapenv:Body>
        </soapenv:Envelope>
        """
        resp = requests.post(url, headers=headers, data=data.format(customerMsisdn= request.data['customerMsisdn'], totalAmount = request.data['totalAmount'], currency=request.data['totalAmount'],amountPerItem = request.data['totalAmount'], 
        description= request.data['totalAmount'], discount= request.data['totalAmount'], apiKey= request.data['totalAmount']))
        print(resp.status_code)
        return Response(resp)
    else:
        queryset = BaiPaga.objects.all()
        serializer_class = BaiPagaSerializer(queryset)
        return Response(serializer_class.data)


@api_view(['GET', 'POST'])
def MulticaixaExpressToken(request):
   
    if request.method == 'POST':
        print('Hello POST Method')
        print(request.data['amount']) 
        url = "https://cerpagamentonline.emis.co.ao/online-payment-gateway/portal/frameToken"

        payload = json.dumps({
        "reference": "A1",
        "amount": request.data['amount'],
        "terminal": "1095",
        "token": "6ad7e8f1-e610-4f11-a79b-501dde4ade88",
        "mobile": "PAYMENT",
        "callbackUrl": "https://webhook.site/64f885ae-4ac9-4c47-98fa-402d186d0955",
        "card": "DISABLED"
        })

        headers = {
        'Content-Type': 'application/json',
        'Cookie': 'cookieserver=cergpogwh1c-portal'
    }

        response = requests.request("POST", url, headers=headers, data=payload)
        resposta = response.text.replace("\"", "'")
        
        return Response(json.loads(response.text))

    else:
        print(request.data) 
        return Response({"message": "Hello, world!"})