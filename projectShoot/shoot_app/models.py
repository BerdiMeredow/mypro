from django.db import models

class Shoot(models.Model):
    ady = models.CharField(max_length=50)
    fam = models.CharField(max_length=50)
    topar = models.CharField(max_length=50)
    pm1_1 = models.IntegerField(blank=True,null=True)
    pm1_2 = models.IntegerField(blank=True,null=True)
    pm2_1 = models.IntegerField(blank=True,null=True)
    pm2_2 = models.IntegerField(blank=True,null=True)
    ak74 = models.IntegerField(blank=True,null=True)
    umumy = models.IntegerField(blank=True,null=True)