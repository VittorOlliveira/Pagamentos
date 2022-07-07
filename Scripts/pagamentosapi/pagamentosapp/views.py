from xml.parsers.expat import model
from django.shortcuts import render
from requests.api import request
#from requests.models import Response
from rest_framework.response import Response

from rest_framework import viewsets
from rest_framework.views import APIView
from .serializers import BaiPagaSerializer, MulticaixaExpressSerializer, ReferencesSerializer
from .models import BaiPaga, MulticaixaExpress, References
import requests
import json
from rest_framework.decorators import action, api_view, parser_classes
from django.views.decorators.csrf import csrf_exempt
from requests.structures import CaseInsensitiveDict
from rest_framework import permissions
import xml.etree.ElementTree as ET

from django.conf import settings
from django.core.mail import send_mail

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from bs4 import BeautifulSoup

import locale
from datetime import date
from dateutil.relativedelta import relativedelta

import redis
import json

from django.http import JsonResponse

from rest_framework.views import APIView
from rest_framework_xml.parsers import XMLParser

from requests.auth import HTTPBasicAuth

from django.forms.models import model_to_dict
import random
import os
from dotenv import load_dotenv
load_dotenv()



# Create your views here.
class BaiPagaModelViewSet(viewsets.ModelViewSet):

    #permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = BaiPaga.objects.all()
    serializer_class = BaiPagaSerializer

    def patch(self, request, validated_data):
        instance = BaiPaga.objects.get(reference=validated_data.pop('reference', None))
        serializer = BaiPagaSerializer(instance, data=request.data, partial=True) # set partial=True to update a data partially
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(code=201, data=serializer.data)
        return JsonResponse(code=400, data="wrong parameters")

#class MulticaixaExpressModelViewSet(viewsets.ModelViewSet):
class MulticaixaExpressModelViewSet(viewsets.ModelViewSet):

    #permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    queryset = MulticaixaExpress.objects.all()
    serializer_class = MulticaixaExpressSerializer

    def patch(self, request, validated_data):
        instance = MulticaixaExpress.objects.get(reference=validated_data.pop('reference', None))
        serializer = MulticaixaExpressSerializer(instance, data=request.data, partial=True) # set partial=True to update a data partially
        if serializer.is_valid():
            serializer.save()
            return JsonResponse(code=201, data=serializer.data)
        return JsonResponse(code=400, data="wrong parameters")

class ReferencesViewSet(viewsets.ModelViewSet):
    queryset = References.objects.all()
    serializer_class = ReferencesSerializer


@api_view(['POST'])
def BaiPagaViewSet(request):
    
    if request.method == 'POST':
        url = "https://ib.bancobai.ao/QUAMDW-3G/internet-banking/api/soap/partners/MobilePaymentsExternalPartnersIntegrationService?wsdl"

        headers = CaseInsensitiveDict()
        headers["Content-Type"] = "application/xml"
        if request.data['app'] != "ACCloud":
            responseOfRedis = redis.StrictRedis(host="10.100.120.44", port="6379", password='AngolaCables2021')
            responseOfRedis.set(str(request.data['reference']), 'PENDENTE')
            tokenApp = {"tokenApp": request.data['tokenApp']}
            x = str(request.data['reference']).split("Y")
            responseOfRedis.set("RefID",  int(x[1]) + 1)

        payload = json.dumps({})
        status = {"status": "PENDENTE"}
        currency = {"currency": "AOA"}
        email = {"email": request.data['email']}
        customerMsisdn = {"customerMsisdn": request.data['customerMsisdn'] }
        apiKey = {"apiKey": '0f98473f-0363-4703-a0b6-d14799f166d9'}
        totalAmount = {"totalAmount": request.data['totalAmount']}
        appCode = {"appCode": "ACCloud"}
        reference = {"reference": request.data['reference']}
        
        payload_internal = json.loads(payload)
        payload_internal.update(customerMsisdn)
        payload_internal.update(apiKey)
        payload_internal.update(totalAmount)
        payload_internal.update(currency)
        payload_internal.update(status)
        payload_internal.update(reference)
        payload_internal.update(email)
        if request.data['app'] != "ACCloud":
            payload_internal.update(tokenApp)
            payload_internal.update(appCode)
        #insert = requests.request("POST", "https://payments.atlanticconnect.com.br/baipaga-billed/", headers = {'Content-Type': 'application/json'}, data=json.dumps(payload_internal))
        data = """
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:com="com.inm.mobilepayments">
                    <soapenv:Header/>
                    <soapenv:Body>
                        <com:initiateMobilePaymentViaOtpRequestFromMerchant>
                            <customerMsisdn>{customerMsisdn}</customerMsisdn>
                            <totalAmount>{totalAmount}</totalAmount>
                            <currency>AKZ</currency>
                            <shoppingCart>q
                                <!--Zero or more repetitions:-->
                                <items>
                                    <!--Optional:-->
                                    <amountPerItem>{amountPerItem}</amountPerItem>
                                    <!--Optional:-->
                                    <count>1</count>
                                    <!--Optional:-->
                                    <description>Plano {description}</description>
                                    <!--Optional:-->
                                    <discount>{discount}</discount>
                                    <!--Optional:-->
                                    <totalAmount>{totalAmount}</totalAmount>
                                </items>
                            </shoppingCart>
                            <!--Optional:-->
                            <externalReference>{reference}</externalReference>
                            <!--Optional:-->
                            <description>Plano {description}</description>
                            <!--Optional:-->
                            <apiKey>0f98473f-0363-4703-a0b6-d14799f166d9</apiKey>
                        </com:initiateMobilePaymentViaOtpRequestFromMerchant>
                    </soapenv:Body>
                </soapenv:Envelope>
        """.format(customerMsisdn= request.data['customerMsisdn'], totalAmount = request.data['totalAmount'], amountPerItem = request.data['totalAmount'], discount=0, description=request.data['description'], reference = request.data['reference'],)

        resp = requests.post(url, headers=headers, data=data)
        tree = ET.fromstring(resp.text)
        body = tree.getchildren()

        if(resp.status_code > 200):
            Fault = body[0].getchildren()
            retornar = Fault[0].getchildren()[1].text
            retornar = retornar.replace("\"", "")
            erro = {"error": retornar}
            baiData = {}
            baiData.update(erro)
        else:
            ns2 = body[0].getchildren()
            ret = ns2[0].getchildren()
            retornar =  ret[0].getchildren()[0].text
            baiData = {}
            operationID = {"operationId": ret[0].getchildren()[1].text}
            retornar = retornar.replace("\"", "")
            link = {"link": retornar}
            baiData.update(link)
            baiData.update(operationID)

        return Response(baiData)
    
    


@api_view(['POST'])
def MulticaixaExpressToken(request):
   
    if request.method == 'POST':
        url = "https://cerpagamentonline.emis.co.ao/online-payment-gateway/portal/frameToken"

        payload = json.dumps({
        "reference": request.data['reference'],
        "amount": request.data['amount'],
        "token": "768ea9c8-9159-4039-b403-ae96f16f4bcc",
        "mobile": "PAYMENT",
        "card": "DISABLED",
        "callbackUrl": "https://payments.atlanticconnect.com.br/callbackExpress/"
        })

        headers = {
        'Content-Type': 'application/json',
        'Cookie': 'cookieserver=cergpogwh1c-portal'
        }

        status = {"status": "PENDENTE"}
        currency = {"currency": "AOA"}
        if request.data['app'] != 'ACCloud':
            email = {"email": request.data['email']}
            tokenApp = {"tokenApp": request.data['tokenApp']}
            payload_internal = json.loads(payload)
            payload_internal.update(status)
            payload_internal.update(currency)
            payload_internal.update(email)
            payload_internal.update(tokenApp)

        if request.data['app'] != 'ACCloud':
            """ Inserido dados do pagamento ao Redis"""
            responseOfRedis = redis.StrictRedis(host="10.100.120.44", port="6379", password='AngolaCables2021')
            dataTo_JSON = {'data': payload_internal}
            responseOfRedis.execute_command('JSON.SET', str(request.data['reference']), '.', json.dumps(dataTo_JSON))
            #responseOfRedis.set(str(request.data['reference']), 'PENDENTE')
            #responseOfRedis.set(str(request.data['reference']), json.dumps(payload_internal))
            x = str(request.data['reference']).split("Y")
            responseOfRedis.set("RefID", int(x[1]) + 1 )
            #insert = requests.request("POST", "https://payments.atlanticconnect.com.br/multicaixaexpress-billed/", headers = {'Content-Type': 'application/json'}, data=json.dumps(payload_internal))
     
        response = requests.request("POST", url, headers=headers, data=payload)
        resposta = response.text.replace("\"", "'")
        
        return Response(json.loads(response.text))


@api_view(['POST'])
def RedisGet(request):
    status = ""
    try:
        responseOfRedis = redis.StrictRedis(host="10.100.120.44", port="6379", password='AngolaCables2021')
        payload_internal = json.loads(responseOfRedis.execute_command('JSON.GET ' + str(request.data["reference"]), 'NOESCAPE', '.data'))
        status = payload_internal['status']
    except:
        print("failed to send to Redis")
    
    return Response(status)

@api_view(['GET'])
def GetPaymentReference(request):
    try:
        responseOfRedis = redis.StrictRedis(host="10.100.120.44", port="6379", password='AngolaCables2021')
        refID = responseOfRedis.get('RefID')
    except:
        print("failed to get from Redis")
    
    return Response(refID)

@api_view(['POST'])
def SetPaymentReference(request):
    res = Response()
    try:
        responseOfRedis = redis.StrictRedis(host="10.100.120.44", port="6379", password='AngolaCables2021')
        responseOfRedis.execute_command('JSON.SET', "AFRICAPLAY999", '.', json.dumps(request.data))
        responseOfRedis.set(str(request.data['reference']), 'PENDENTE')
        res.status_code = 200
        res.code = "success"
    except:
        print("failed to get from Redis")
        #print(responseOfRedis)
        res.status_code = 400
        res.code = "failure"
    
    return res


@api_view(['POST'])
@parser_classes((XMLParser,))
def CallbackBai(request, format=None):
    url = "https://ib.bancobai.ao/QUAMDW-3G/internet-banking/api/soap/partners/MobilePaymentsExternalPartnersIntegrationService?wsdl"

    headers = CaseInsensitiveDict()
    headers["Content-Type"] = "application/xml"

    data = """
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:com="com.inm.mobilepayments">
        <soapenv:Header/>
        <soapenv:Body>
        <com:getMobilePaymentRequestFromMerchantStatus>
        <!--Optional:-->
        <!--Optional:-->
        <paymentId>50</paymentId>
        <!--Optional:-->
        <apiKey>0f98473f-0363-4703-a0b6-d14799f166d9</apiKey>
        </com:getMobilePaymentRequestFromMerchantStatus>
        </soapenv:Body>
        </soapenv:Envelope>
    """
    resp = requests.post(url, headers=headers, data=data)
    tree = ET.fromstring(resp.text)
    body = tree.getchildren()
    Fault = body[0].getchildren()
    print(Fault[0].getchildren()[1].text)
    body = tree.getchildren()
    
    if(resp.status_code > 200):
            Fault = body[0].getchildren()
            retornar = Fault[0].getchildren()[1].text
            retornar = retornar.replace("\"", "")
            erro = {"error": retornar}
            baiData = {}
            baiData.update(erro)
    else:
            ns2 = body[0].getchildren()
            ret = ns2[0].getchildren()
            print(ret)
            retornar =  ret[0].getchildren()[0].text
            print(ret[0].getchildren()[1].text)
            baiData = {}
            operationID = {"operationId": ret[0].getchildren()[1].text}
            retornar = retornar.replace("\"", "")
            link = {"link": retornar}
            baiData.update(link)
            baiData.update(operationID)

    if request.method == 'POST':
        data = request.data
        instance = BaiPaga.objects.filter(reference=data['externalReference'])
        for obj in instance:
            print(obj)

        if data['status'] == 'SUCCESS':
            responseOfRedis = redis.StrictRedis(host="10.100.120.44", port="6379", password='AngolaCables2021')
            responseOfRedis.set(str(data['externalReference']), 'SUCCESS')
            instance = BaiPaga.objects.filter(reference=data['externalReference'])
            
            insert = requests.request("PATCH", "https://payments.atlanticconnect.com.br/baipaga-billed/" + str(instance[0].id) + "/", headers = {'Content-Type': 'application/json'}, data=json.dumps({"status": data['status']}))
            params = {'email': instance[0].email}
            res = requests.request("POST", "https://apiportalmedia.atlanticconnect.com.br/user-active-subscription/", params=params, headers = {'Authorization': 'Bearer '+ str(instance[0].tokenApp)})
            user = res.json()
            fromaddr = "vasconsellosolliveira@gmail.com"
            toaddr = instance[0].email

            today = date.today()

            html = open("./Recibo.html")
            soup = BeautifulSoup(html.read())
            #found_data = soup.find(class_='preheader')
            #found_data.string = 'Este é um recibo da sua subscrição recente em ' + today.strftime("%d/%m/%Y")
            found_data = soup.find(class_='ola')
            found_data.string = 'Olá ' + user['nomeCompleto']+','
            found_data = soup.find(class_='receipt_number')
            found_data.string = data['externalReference']
            found_data = soup.find(class_='purchase_item')
            found_data.string = 'Plano ' + user['plano']
            found_data = soup.find(class_='price')
            found_data.string = str(user['totalComIVA']) + ' AOA'
            found_data = soup.find(class_='priceTotal')
            found_data.string = ' '+str(user['totalComIVA']) + ' AOA'
           
            #search_text = 'purchase_date'
            #soup.find(text=lambda x: x.startswith(search_text)).replaceWith(today.strftime("%d/%m/%Y"))
            
            msg = MIMEText(soup, 'html')
            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = "Subscrição conluída"

            debug = False
            if debug:
                print(msg.as_string())
            else:
                server = smtplib.SMTP('smtp.gmail.com',587)
                server.starttls()
                server.login("vasconsellosolliveira@gmail.com", "21430870Olly100295")
                text = msg.as_string()
                server.sendmail(fromaddr, toaddr, text)
                server.quit()
        else:
            instance = BaiPaga.objects.filter(reference=data['externalReference'])
            insert = requests.request("PATCH", "https://payments.atlanticconnect.com.br/baipaga-billed/" + str(instance[0].id) + "/", headers = {'Content-Type': 'application/json'}, data=json.dumps({"status": data['status']}))
            responseOfRedis = redis.StrictRedis(host="10.100.120.44", port="6379", password='AngolaCables2021')
            responseOfRedis.set(str(data['externalReference']), 'REJECTED')
            params = {'email': instance[0].email}
            res = requests.request("POST", "https://apiportalmedia.atlanticconnect.com.br/user-active-subscription/", params=params, headers = {'Authorization': 'Bearer '+ str(instance[0].tokenApp)})
            user = res.json()

            fromaddr = "vasconsellosolliveira@gmail.com"
            toaddr = instance[0].email

            today = date.today()

            html = open("./Recibo2.html")
            soup = BeautifulSoup(html.read())
            #found_data = soup.find(class_='preheader')
            #found_data.string = 'Este é um recibo da sua subscrição recente em ' + today.strftime("%d/%m/%Y")
            found_data = soup.find(class_='ola')
            found_data.string = 'Olá ' + user['nomeCompleto']+','
            
           
            #search_text = 'purchase_date'
            #soup.find(text=lambda x: x.startswith(search_text)).replaceWith(today.strftime("%d/%m/%Y"))
            
            msg = MIMEText(soup, 'html')
            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = "Subscrição nã concluída"

            debug = False
            if debug:
                print(msg.as_string())
            else:
                server = smtplib.SMTP('smtp.gmail.com',587)
                server.starttls()
                server.login("vasconsellosolliveira@gmail.com", "21430870Olly100295")
                text = msg.as_string()
                server.sendmail(fromaddr, toaddr, text)
                server.quit()


        json_data = json.dumps(data)
        Response(json_data.replace("\"", "'"))
        return Response(request.data.get('status'))
    else:
        return Response(request.data)


@api_view(['POST'])
def CallbackExpress(request):
    if request.method == 'POST':
        data = request.data
        callback_data = {}
        callback_data["reference"] = request.data.get('reference')
        if data.get('status') == "ACCEPTED":

            responseOfRedis = redis.StrictRedis(host="10.100.120.44", port="6379", password='AngolaCables2021')
            payload_internal = json.loads(responseOfRedis.execute_command('JSON.GET ' + str(data["reference"]['id']), 'NOESCAPE', '.data'))

            status = {"status": "ACCEPTED"}
            payload_internal.update(status)

            #print(payload_internal)

            dataTo_JSON = {'data': payload_internal}
            responseOfRedis.execute_command('JSON.SET', str(request.data['reference']), '.', json.dumps(dataTo_JSON))

            """ Recuperando dados do cliente """
            params = {'email': payload_internal["email"]}
            user = requests.request("GET", "https://apiportalmedia.atlanticconnect.com.br/user/", params=params, headers = {'Authorization': 'Bearer '+ payload_internal["tokenApp"]})
            #user = requests.request("GET", "http://10.100.120.18:8016/user/", params=params, headers = {'Authorization': 'Bearer '+ payload_internal["tokenApp"]})

            user = user.json()
            #print(user)

            """ Recuperando planos """
            planos = requests.request("GET", "https://apiportalmedia.atlanticconnect.com.br/planos/", headers = {'Authorization': 'Bearer '+ payload_internal["tokenApp"]})
            #planos = requests.request("GET", "http://10.100.120.18:8016/planos/", headers = {'Authorization': 'Bearer '+ payload_internal["tokenApp"]})
            planos = planos.json()

            tipoPlano = " "
            planoID = 3
            for x in planos:
                if x['preco'] == float(payload_internal['amount']):
                    tipoPlano = x['tipo']  
                    planoID = x['id'] 

            """ Preparando a data de início e fim da subscrição """
            today = date.today()
            future_date = today + relativedelta(months=1)

            """ Assinando subscrição para o User"""
            body = {"user": user[0]['id'],
                    "plano": planoID,
                    "totalSemIVA": payload_internal['amount'],
                    "totalComIVA": payload_internal['amount'],
                    "subscriptionDate": today.strftime("%Y-%m-%d"),
                    "subscriptionExpirationDate": future_date.strftime("%Y-%m-%d")
            }

            subscription = requests.request("POST", "https://apiportalmedia.atlanticconnect.com.br/subscription/", data = body, headers = {'Authorization': 'Bearer '+ payload_internal["tokenApp"]})      

            """ Enviando Email Usuário """
            fromaddr = "vasconsellosolliveira@gmail.com"
            toaddr = payload_internal["email"]

            today = date.today()

            html = open("./Recibo.html")
            soup = BeautifulSoup(html.read())
            found_data = soup.find(class_='ola')
            found_data.string = 'Olá ' + user[0]['first_name']+' '+ user[0]['last_name'] + ', '
            found_data = soup.find(class_='receipt_number')
            found_data.string = payload_internal["reference"]
            found_data = soup.find(class_='purchase_item')
            found_data.string = 'Plano ' + str(tipoPlano)
            found_data = soup.find(class_='price')
            found_data.string = str(payload_internal["amount"]) + ' AOA'
            found_data = soup.find(class_='priceTotal')
            found_data.string = ' '+str(payload_internal["amount"]) + ' AOA'
                       
            msg = MIMEText(soup, 'html')
            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = "Subscrição conluída"

            debug = False
            if debug:
                print(msg.as_string())
            else:
                server = smtplib.SMTP('smtp.gmail.com',587)
                server.starttls()
                server.login("vasconsellosolliveira@gmail.com", "21430870Olly100295")
                text = msg.as_string()
                server.sendmail(fromaddr, toaddr, text)
                server.quit()
        else:
            responseOfRedis = redis.StrictRedis(host="10.100.120.44", port="6379", password='AngolaCables2021')
            payload_internal = json.loads(responseOfRedis.execute_command('JSON.GET ' + str(data["reference"]['id']), 'NOESCAPE', '.data'))

            status = {"status": "REJECTED"}
            payload_internal.update(status)
            dataTo_JSON = {'data': payload_internal}
            responseOfRedis.execute_command('JSON.SET', str(request.data['reference']), '.', json.dumps(dataTo_JSON))
            #print(payload_internal)
            
            """ Recuperando dados do cliente """
            params = {'email': payload_internal["email"]}
            user = requests.request("GET", "https://apiportalmedia.atlanticconnect.com.br/user/", params=params, headers = {'Authorization': 'Bearer '+ payload_internal["tokenApp"]})
            user = user.json()
            print(user)

            """ Enviando Email Usuário """
            fromaddr = "vasconsellosolliveira@gmail.com"
            toaddr = payload_internal["email"]

            today = date.today()
            html = open("./Recibo2.html")
            soup = BeautifulSoup(html.read())
           
            found_data = soup.find(class_='ola')
            found_data.string = 'Olá ' + user[0]['first_name']+' '+ user[0]['last_name'] + ', '
            
            msg = MIMEText(soup, 'html')
            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = "Subscrição nã concluída"

            debug = False
            if debug:
                print(msg.as_string())
            else:
                server = smtplib.SMTP('smtp.gmail.com',587)
                server.starttls()
                server.login("vasconsellosolliveira@gmail.com", "21430870Olly100295")
                text = msg.as_string()
                server.sendmail(fromaddr, toaddr, text)
                server.quit()


        json_data = json.dumps(callback_data)
        Response(json_data.replace("\"", "'"))
        return Response(request.data.get('status'))
    else:
        return Response(request.data)


@api_view(['POST'])
def MailPaypalUser(request):

        if request.data['status'] == "APPROVE":

            """ Enviando Email Usuário """
            fromaddr = "vasconsellosolliveira@gmail.com"
            toaddr = request.data["email"]

            today = date.today()

            html = open("./Recibo.html")
            soup = BeautifulSoup(html.read())
            found_data = soup.find(class_='ola')
            found_data.string = 'Olá ' + request.data['nome'] + ', '
            found_data = soup.find(class_='receipt_number')
            found_data.string = "1 Enterprise Subscription"
            found_data = soup.find(class_='purchase_item')
            found_data.string = 'Plano ' + request.data['plano']
            found_data = soup.find(class_='price')
            found_data.string = str(request.data['price']) + ' ' + request.data['moeda']
            found_data = soup.find(class_='priceTotal')
            found_data.string = ' '+ str(request.data['price']) + ' ' + request.data['moeda']
                       
            msg = MIMEText(soup, 'html')
            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = "Subscrição conluída"

            debug = False
            if debug:
                print(msg.as_string())
            else:
                server = smtplib.SMTP('smtp.gmail.com',587)
                server.starttls()
                server.login("vasconsellosolliveira@gmail.com", "21430870Olly100295")
                text = msg.as_string()
                server.sendmail(fromaddr, toaddr, text)
                server.quit()
                
        else:

            """ Enviando Email Usuário """
            fromaddr = "vasconsellosolliveira@gmail.com"
            toaddr =  request.data["email"]

            today = date.today()
            html = open("./Recibo2.html")
            soup = BeautifulSoup(html.read())
           
            found_data = soup.find(class_='ola')
            found_data.string = 'Olá ' + request.data['nome'] + ', '
            
            msg = MIMEText(soup, 'html')
            msg['From'] = fromaddr
            msg['To'] = toaddr
            msg['Subject'] = "Subscrição nã concluída"

            debug = False
            if debug:
                print(msg.as_string())
            else:
                server = smtplib.SMTP('smtp.gmail.com',587)
                server.starttls()
                server.login("vasconsellosolliveira@gmail.com", "21430870Olly100295")
                text = msg.as_string()
                server.sendmail(fromaddr, toaddr, text)
                server.quit()


        return Response('Email Sent', status=200)

@api_view(['GET'])
def generateReference(request):
    first = random.randint(1,9)
    first = str(first)
    n = 9

    nrs = [str(random.randrange(10)) for i in range(n-1)]
    for i in range(len(nrs)):
        first += str(nrs[i])

    return Response(first)

def generateRef():
    first = random.randint(1,9)
    first = str(first)
    n = 9

    nrs = [str(random.randrange(10)) for i in range(n-1)]
    for i in range(len(nrs)):
        first += str(nrs[i])

    return first



@api_view(['POST'])
def RequestReference(request):
    first = generateRef()
    url = "https://api.proxypay.co.ao/references/"
    APIKey = os.getenv('ProxyPayAPIKey')

    ref = [x for x in References.objects.filter(reference=first)]
        
    if ref:
        first = generateRef()
    else:
        #data = {}
        #data['reference'] = first
        #data['user_id'] = request.data['custom_fields']['user_id']
        

        payload = json.dumps(request.data)

        headers = {
        'Accept': 'application/vnd.proxypay.v2+json',
        'Authorization': 'Token baanijjpsb40nh2ie8n06om8hcshv6uq',
        'Content-Type': 'application/json'
        }

        exchangeHeaders = {
                'Accept': 'application/json',
                'Content-Type': 'application/json',
                'Authorization': "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoyOTE4MzkyODU1LCJpYXQiOjE2NTY5NTI4NTUsImp0aSI6Ijk0OTQxYjRjNDBiNzRjOGU5YTk3YjJjMDdkNDhlNDNkIiwidXNlcl9pZCI6M30.Ts18-BoAz6Mr544Wq7inqnaYZMzqHKLyArtcmT4nOs8",
            }

        exchangeUrl = 'http://10.100.120.18:8022/exchangefromhome/'
        exchangeRate = requests.request("GET", exchangeUrl, headers=exchangeHeaders)

        convertedBalance = ""
        balanceUSD = ""
        if request.data['custom_fields']['currency'] == "USD":
            balanceUSD = request.data['amount']
            convertedBalance = int(request.data['amount']) * float(exchangeRate.text)
            payload=json.loads(payload)
            convertedBalance = float("{:.2f}".format(convertedBalance))
            payload.update({'amount': convertedBalance})
            payload = json.dumps(payload)
        else:
            convertedBalance = int(request.data['amount']) / float(exchangeRate.text)
            balanceUSD = float("{:.2f}".format(convertedBalance))

        response = requests.request("PUT", url + first, headers=headers, data=payload)
        #obj = References.objects.create(data)
        #print(obj.text)
        if response.status_code == 204:
            payload = json.loads(payload)
            payload.update({'reference': first})

            # Registar na API do AC Cloud 
            headers = {
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoyOTE4MzkyODU1LCJpYXQiOjE2NTY5NTI4NTUsImp0aSI6Ijk0OTQxYjRjNDBiNzRjOGU5YTk3YjJjMDdkNDhlNDNkIiwidXNlcl9pZCI6M30.Ts18-BoAz6Mr544Wq7inqnaYZMzqHKLyArtcmT4nOs8',
            'Content-Type': 'application/json'
            }

            body = json.dumps({
                "entity": "277",
                "reference": payload['reference'],
                "value": payload['amount'],
                "valueUSD": balanceUSD,
                "validUntil": str(date.today() + relativedelta(days = 2)),
                "state": "Por pagar",
                "zadaraID": 1,
                "user": payload['custom_fields']['user_id']
            })

            url = "http://10.100.120.18:8022/referencehistory/"
            res = requests.request("POST", url, headers=headers, data=body)
            print(res.text)
            refObj = json.loads(res.text)
            print(refObj['id'])
            data = References(reference= first, user_id=request.data['custom_fields']['user_id'], reference_id = refObj['id'], valueUSD=balanceUSD)
            data.save()
            ref = ReferencesSerializer(data=data)
            if ref.is_valid():
                ref.save()
            
            return Response(payload)
        else:
            return Response({"Error": "Erro"}, status=response.status_code)


    return  Response({"reference ": first}, status=200)


@api_view(['POST'])
def CallbackExpressCloud(request):
    if request.method == 'POST':
        instance = References.objects.get(reference=request.data['reference']['id'])
        serializer_class = ReferencesSerializer(instance)
        print(serializer_class.data)
        # Registar na API do AC Cloud 
        headers = {
            'Authorization': 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoyOTE4MzkyODU1LCJpYXQiOjE2NTY5NTI4NTUsImp0aSI6Ijk0OTQxYjRjNDBiNzRjOGU5YTk3YjJjMDdkNDhlNDNkIiwidXNlcl9pZCI6M30.Ts18-BoAz6Mr544Wq7inqnaYZMzqHKLyArtcmT4nOs8',
            'Content-Type': 'application/json'
        }

        body = json.dumps({
                "reference": request.data['reference']['id'],
                'value': request.data['amount'],
                "status": "Pago",
                "user": serializer_class.data['user_id']
            })
        url = "http://10.100.120.18:8022/referencehistory/"
        res = requests.request("POST", url, headers=headers, data=body)

    return  Response(res.json())

