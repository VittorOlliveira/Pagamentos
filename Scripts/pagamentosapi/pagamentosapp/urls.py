from django.urls import include, path
from rest_framework import routers
from . import views

router = routers.DefaultRouter()
router.register(str('baipaga-billed'), views.BaiPagaModelViewSet)
router.register(str('multicaixaexpress-billed'), views.MulticaixaExpressModelViewSet)
router.register(str('references'), views.ReferencesViewSet)



# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('baipaga/', views.BaiPagaViewSet, name='baipaga'),
    path('multicaixaexpress/', views.MulticaixaExpressToken, name='multicaixaexpress'),
    path('callbackExpress/', views.CallbackExpress),
    path('callbackCloud/', views.CallbackExpressCloud),
    path('callbackBai/', views.CallbackBai),
    path('getPaymentStatus/', views.RedisGet),
    path('getRefID/', views.GetPaymentReference),
    path('setRefID/', views.SetPaymentReference),
    path('mailPaypal/', views.MailPaypalUser),
    path('getReference/', views.RequestReference),
    path('generateReference/', views.generateReference),

    ]