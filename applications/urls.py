from django.urls import path
from . import views

urlpatterns = [
    path('', views.MainPageView, name='index'),
    path('app/<str:model_name>/', views.GeneralModelView, name="indvi_models"),
    path('app/<str:model_name>/update/<int:id>/', views.GeneralModelUpdateView, name="indvi_models_update"),
    path('app/<str:model_name>/delete/<int:id>/', views.GeneralModelDeleteView, name="indvi_models_delete"),
]
