import django_tables2 as tables
from .models import GCAS

class GCASTable(tables.Table):
    class Meta:
        model = GCAS
        template_name = 'django_tables2/bootstrap.html'
