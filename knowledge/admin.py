from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from .models import Seed, Document_Seed, SDG, SDG_Seed, Value_chain, Industry, Value_Chain_Seed, Industry_Seed, Comment_Seed, Vision

# all the models that need to be accessed on Admin

admin.site.register(SDG)
admin.site.register(Value_chain)
admin.site.register(Industry)
admin.site.register(Document_Seed)
admin.site.register(Seed)
admin.site.register(Comment_Seed, MPTTModelAdmin)
admin.site.register(SDG_Seed)
admin.site.register(Value_Chain_Seed)
admin.site.register(Industry_Seed)
admin.site.register(Vision)
