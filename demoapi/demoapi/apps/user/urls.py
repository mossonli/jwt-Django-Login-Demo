from django.urls import path
from rest_framework_jwt.views import obtain_jwt_token
urlpatterns = [
    # path('admin/', admin.site.urls),
    path(r"login/", obtain_jwt_token),
]
