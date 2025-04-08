from django.urls import path
from . import views
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
  path('recommendations/<int:product_id>/', views.RecommendationView.as_view(), name='recommendations'),
]
