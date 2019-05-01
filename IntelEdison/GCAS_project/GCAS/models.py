# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class GCAS(models.Model):
    temperature = models.FloatField(null=True, blank=True, default=None)
    prediction = models.IntegerField(null=True, blank=True, default=None)
    action = models.CharField(max_length=80, null=True, blank=True, default=None)
    expected = models.CharField(max_length=80, null=True, blank=True, default=None)
