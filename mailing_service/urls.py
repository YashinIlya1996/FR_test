from django.urls import path
from . import views

urlpatterns_mailing = [
    path('mailing/', views.MailingCreateListView.as_view(), name='mailing-list'),
]

urlpatterns_client = [
    path('client/', views.ClientListCreateView.as_view(), name='client-list'),
    path('client/<int:pk>/', views.ClientUDView.as_view(), name='client-cud'),
]

urlpatterns = urlpatterns_mailing + urlpatterns_client
