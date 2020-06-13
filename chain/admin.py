from django.contrib import admin
from .models import Regestration , Transaction , feedback
# Register your models here.

class RegisterAdmin(admin.ModelAdmin):
    list_display = ('u_hash','name','amount')


admin.site.register(Regestration,RegisterAdmin)
admin.site.register(Transaction)
admin.site.register(feedback)
