from django.urls import path
from . import views

urlpatterns_mailing = [
    path('mailing/', views.MailingListView.as_view(), name='mailing-list'),
]

urlpatterns_client = [
    path('client/', views.ClientListView.as_view(), name='client-list'),
    path('client/create/', views.ClientCreateView.as_view(), name='client-create'),
]

urlpatterns = urlpatterns_mailing + urlpatterns_client
