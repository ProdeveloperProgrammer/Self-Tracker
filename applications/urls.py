from django.urls import path,include
from . import views

urlpatterns = [
    path('',views.MainPageView,name='index'),
    path('app/<str:model_name>/',views.GeneralModelView,name="indvi_models"),
    path('app/<str:model_name>/<int:id>/update/',views.GeneralModelUpdateView,name="indvi_models_update"),
    path('app/<str:model_name>/<int:id>/delete/',views.GeneralModelDeleteView,name="indvi_models_delete")
]