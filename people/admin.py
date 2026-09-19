from django.contrib import admin
from .models import Department, Member

admin.site.register([Department, Member])

# Register your models here.
