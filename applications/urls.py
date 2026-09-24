from django.urls import path
from . import views
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('',login_required(views.MainPageView),name='index'),
    path('app/<str:model_name>/',login_required(views.GeneralModelView),name="indvi_models"),
    path('app/<str:model_name>/<int:id>/update/',login_required(views.GeneralModelUpdateView),name="indvi_models_update"),
    path('app/<str:model_name>/<int:id>/delete/',login_required(views.GeneralModelDeleteView),name="indvi_models_delete")
]