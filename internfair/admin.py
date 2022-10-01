from django.contrib import admin

from .models import StartUps,Students, User

from import_export.admin import ImportExportModelAdmin



@admin.register(StartUps)
class StartUpsAdmin(ImportExportModelAdmin):
    pass

@admin.register(Students)
class StudentsAdmin(ImportExportModelAdmin):
    pass

@admin.register(User)
class UserAdmin(ImportExportModelAdmin):
    pass
# Register your models here.
