from django.urls import path
from . import views

urlpatterns_mailing = [
    path('mailing/', views.MailingListCreateView.as_view(), name='mailing-list'),
    path('mailing/<int:pk>', views.MailingUDView.as_view(), name='mailing-retrieve'),
]

urlpatterns_client = [
    path('client/', views.ClientListCreateView.as_view(), name='client-list'),
    path('client/<int:pk>/', views.ClientUDView.as_view(), name='client-retrieve'),
]

urlpatterns = urlpatterns_mailing + urlpatterns_client
