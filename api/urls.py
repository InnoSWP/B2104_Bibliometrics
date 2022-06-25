from django.urls import path
from .views import get, update


urlpatterns = [
	path('get/<str:name>/<str:token>', get, name='post'),
	path('update/<str:token>', update)
]
