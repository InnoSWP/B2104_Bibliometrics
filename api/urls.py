from django.urls import path
from .views import get, update


urlpatterns = [
	path('get/<str:name>/<str:token>', get, name='get'),
	path('update/<str:token>', update, name='post')
]