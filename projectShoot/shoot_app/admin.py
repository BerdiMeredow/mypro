from django.contrib import admin
from . import models

@admin.register(models.Shoot)
class Shoot(admin.ModelAdmin):
    list_display=('ady','fam','topar','pm1_1','pm1_2','pm2_1','pm2_2','ak74','umumy')