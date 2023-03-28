from django.contrib import admin
from .models import *

admin.site.register(Subject)
admin.site.register(Class)
admin.site.register(Test)
admin.site.register(Mark)
admin.site.register(Average)
admin.site.register(Rank)