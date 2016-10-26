from django.conf.urls import url
from mqqs import views

urlpatterns = [
    url(r'^hello$', views.hello),
]