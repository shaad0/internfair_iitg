from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin



@admin.register(Intern_form)
class Intern_formAdmin(ImportExportModelAdmin):
    pass

@admin.register(InternApplication)
class InternApplicationAdmin(ImportExportModelAdmin):
    pass