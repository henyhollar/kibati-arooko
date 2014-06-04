from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin


from .models import ArookoUser

admin.site.register(ArookoUser, UserAdmin)
