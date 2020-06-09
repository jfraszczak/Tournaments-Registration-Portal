from django.contrib import admin
from .models import *

admin.site.register(Tournament)
admin.site.register(Sponsor)
admin.site.register(Sponsoring)
admin.site.register(Participation)
admin.site.register(Match)