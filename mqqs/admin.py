from django.contrib import admin
from mqqs.models import Mqq

class MqqAdmin(admin.ModelAdmin):
    list_display   = ('alias', 'env', 'type', 'deep')
    list_filter    = ('alias','env',)
    ordering       = ('alias', )
    search_fields  = ('alias', 'env')
    
admin.site.register(Mqq, MqqAdmin)
