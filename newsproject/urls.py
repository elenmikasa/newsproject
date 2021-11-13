
from django.contrib import admin
from django.urls import path, include
from .views import helloworldfunc
from .views import HelloWorldClass

urlpatterns = [
    path('admin/', admin.site.urls),
    #path('', include('newsapp.urls')),
    path('helloworldurl',helloworldfunc),
    path('helloworldurl2',HelloWorldClass.as_view()),
    path('',include('newsapp.urls')),
]
