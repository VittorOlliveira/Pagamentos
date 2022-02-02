from django.urls import include, path
from rest_framework import routers
from . import views

#router = routers.DefaultRouter()
#router.register(str('baipaga'), views.BaiPagaViewSet)
#baipaga = views.BaiPagaViewSet.as_view({
#    'get': 'list',
#    'post': 'BaiExternalRequest'
#})


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [

    path('baipaga/', views.BaiPagaViewSet, name='baipaga'),
    path('multicaixaexpress/', views.MulticaixaExpressToken, name='multicaixaexpress'),
    #path('', include(router.urls)),

    ]