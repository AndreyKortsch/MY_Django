from django.urls import path
from .views import CountryListCreate, CountryDetail,ManufacturerListCreate,ManufacturerDetail,CarListCreate,CarDetail,CommentListCreate,CommentDetail,CommentCreate
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('country/', CountryListCreate.as_view(), name='country-list'),
    path('country/<str:pk>/', CountryDetail.as_view(), name='country-detail'),
    path('manufacturer/', ManufacturerListCreate.as_view(), name='country-list'),
    path('manufacturer/<str:pk>/', ManufacturerDetail.as_view(), name='country-detail'),
    path('car/', CarListCreate.as_view(), name='car-list'),
    path('car/<str:pk>/', CarDetail.as_view(), name='car-detail'),
    path('comment/', CommentListCreate.as_view(), name='comment-list'),
    path('comment/<int:pk>/', CommentDetail.as_view(), name='comment-detail'),
]