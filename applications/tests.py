from .models import Certificate
import json

# 1. Dynamically grab all model field names except 'id'
field_names = [field.name for field in Certificate._meta.ve if field.name != 'id']

# 2. Query the database and pass the fields using unpacking (*)
TotalData = list(Certificate.objects.all().order_by('-id').values_list(*field_names))
print(TotalData)