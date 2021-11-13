from django.urls import path
from .views import Create, listfunc,ignorelist,demo3,TalentView,TalentListView,Delete,MemberList,CheckView
from .views import TalentCreate


urlpatterns = [
    path('', Create.as_view(), name='home'),
    path('list/', listfunc, name='list'),
    path('list/<int:num>', listfunc, name='list'),
    path('ignorelist/', ignorelist, name='ignorelist'),
    path('station/', demo3, name='station'),
    path('talent/', TalentView.as_view(), name='talent'),
    #path('talentlist/', TalentListView.as_view(), name='talentlist'),
    path('talentlist/', MemberList.as_view(), name='member'),
    #path('talentlist/<int:num>', MemberList.as_view(), name='member'),
    path('delete/<int:pk>/', Delete.as_view(), name='delete'),
    path('check/', CheckView.as_view(), name='check'),
    path('talentcreate/', TalentCreate.as_view(), name='talentcreate'),
]