from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
# from apps.admin import event_admin_site

from root.settings import STATIC_ROOT,STATIC_URL

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.urls'))
    # path('event-admin/', event_admin_site.urls),
] + static(STATIC_URL, document_root=STATIC_ROOT)