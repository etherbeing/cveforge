from django.contrib import admin
from .models import SoftwareModel, HostModel, CVEModel
# Register your models here.
@admin.register(SoftwareModel)
class SoftwareAdmin(admin.ModelAdmin):
    pass

@admin.register(HostModel)
class HostAdmin(admin.ModelAdmin):
    pass

@admin.register(CVEModel)
class CVEAdmin(admin.ModelAdmin):
    pass
