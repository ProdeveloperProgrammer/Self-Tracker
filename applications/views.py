from django.shortcuts import render, redirect,get_object_or_404
from django.core.serializers import serialize
from django.apps import apps
from .models import *
from django import forms, http
from django.forms.models import model_to_dict
import json
# Create your views here.


def MainPageView(request):
    app_config = apps.get_app_config('applications')
    models_list = list(app_config.get_models())

    # This returns an iterable of model classes
    context = {
        "appli": [],
    }
    for model in models_list:
        context['appli'].append((model.__name__))
    return render(request, 'index.html', context=context)


def GeneralModelView(request, model_name):

    # Loading the model in views.py
    try:
        MyModel = apps.get_model(app_label='applications', model_name=model_name)
    except LookupError:
        raise http.Http404("Model does not exist")

    # Loading the Form for making new / updating previous
    DynamicForm = forms.modelform_factory(MyModel, fields='__all__')

    if request.method == 'GET':
        form = DynamicForm()
        fields_name_to_show = [field.verbose_name for field in MyModel._meta.fields] # getting the fields of mdodel

        context = {
            "model_name": model_name,
            "form":form,
            "fields":fields_name_to_show,
        }

        TotalData = MyModel.objects.all().order_by('-id')
        context['rows'] = list(TotalData.values_list())
        return render(request, 'subpage.html', context=context)
    elif request.method == 'POST':
        # Bind the POST data (and FILES if your model handles images/files)
        form = DynamicForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('indvi_models',model_name=model_name)
        else:
            return http.HttpResponse("Error")
    else:
        return redirect("index")

def GeneralModelUpdateView(request,model_name,id):
    # Loading the model in views.py
    try:
        MyModel = apps.get_model(app_label='applications', model_name=model_name)
    except LookupError:
        raise http.Http404("Model does not exist")

    # Loading the Form for making new / updating previous
    DynamicForm = forms.modelform_factory(MyModel, fields='__all__')

    # Bind the POST data (and FILES if your model handles images/files)
    instance = get_object_or_404(MyModel, id=id)
    form = DynamicForm(request.POST, request.FILES,instance=instance)
    if form.is_valid():
        MyModel.objects.filter(id=id).update(**form.cleaned_data)
        return redirect('indvi_models',model_name=model_name)
    else:
        print(form.errors)
        return http.HttpResponse("Error")


def GeneralModelDeleteView(request,model_name,id):
    # Loading the model in views.py
    try:
        MyModel = apps.get_model(app_label='applications', model_name=model_name)
    except LookupError:
        raise http.Http404("Model does not exist")

    if request.method == "POST":
        instance = get_object_or_404(MyModel, id=id)
        MyModel.objects.filter(id=id).delete()
        instance.delete()
        
    return redirect('indvi_models',model_name=model_name)