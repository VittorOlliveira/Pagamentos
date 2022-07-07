from django.contrib import admin

from pagamentosapp.models import BaiPaga, MulticaixaExpress, References

# Register your models here.
admin.site.register(BaiPaga)
admin.site.register(MulticaixaExpress)
admin.site.register(References)
