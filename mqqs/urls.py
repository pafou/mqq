from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_swagger.views import get_swagger_view

from mqqs import views

schema_view = get_swagger_view(title='Pastebin API')

urlpatterns = [
    url(r'^$', views.MqqList.as_view()),
    url(r'^(?P<pk>[0-9]+)/$', views.MqqDetail.as_view()),
    url(r'^doc$', schema_view)

]

urlpatterns = format_suffix_patterns(urlpatterns)