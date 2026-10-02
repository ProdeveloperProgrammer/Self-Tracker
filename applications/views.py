from django.shortcuts import render, redirect,get_object_or_404
from django.apps import apps
from django import forms
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from django.core.exceptions import ValidationError
# Create your views here.
Paginator_per_count = 15
# HTML5 Date/Time widget callback setup
def html5_input_callback(db_field, **kwargs):
    if isinstance(db_field, models.TimeField):
        kwargs['widget'] = forms.TimeInput(attrs={'type': 'time'}, format='%H:%M')
    elif isinstance(db_field, models.DateField):
        kwargs['widget'] = forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d')
    elif isinstance(db_field, models.DateTimeField):
        kwargs['widget'] = forms.DateTimeInput(attrs={'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M')
    return db_field.formfield(**kwargs)

# Helper to select template and enrich model-specific context
def get_model_render_config(model_name, context,user):
        if model_name == "finance":
            template_name = "finance.html"
        else:
            template_name = "subpage.html"
        return template_name, context

@login_required
def MainPageView(request):
    app_config = apps.get_app_config('applications')
    models_list = list(app_config.get_models())

    # This returns an iterable of model classes
    context = {
        "appli": {}
    }
    for model in models_list:
        context['appli'].update({(model._meta.verbose_name):(model._meta.model_name)}) # model name to show and then the link
    return render(request, 'index.html', context=context)

@login_required
def GeneralModelView(request, model_name, id=None):
    # For Viewing the general model and making new entries

    # Dynamically load model
    try:
        MyModel = apps.get_model(app_label='applications', model_name=model_name)
    except LookupError:
        messages.error(request, f"Error: Model '{model_name}' does not exist.")
        return redirect("index")

    DynamicForm = forms.modelform_factory(MyModel, fields='__all__', formfield_callback=html5_input_callback)

    # Model field table headers
    fields_name_to_show = [field.verbose_name for field in MyModel._meta.fields]
    if 'User' in fields_name_to_show:
        fields_name_to_show.remove('User')

    # Fetch data for table
    TotalData = MyModel.objects.filter(User=request.user).order_by('-id')
    page_obj = Paginator(TotalData.values_list(), Paginator_per_count).get_page(request.GET.get('page'))

    # Check if editing an existing instance
    instance = None
    item_id = id or request.POST.get('item_id')
    if item_id:
        instance = get_object_or_404(MyModel, pk=item_id, User=request.user)

    # Handle Requests
    if request.method == 'POST':
        form = DynamicForm(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            inst = form.save(commit=False)
            inst.User = request.user
            try:
                inst.save()
                form.save_m2m()
                messages.success(request, f"Record {'updated' if instance else 'created'} successfully.")
                return redirect('indvi_models', model_name=model_name)
            except ValidationError as e:
                show_modal = True
                messages.error(request,e)
                if hasattr(e, 'error_dict'):
                    for field, error_list in e.error_dict.items():
                        for error in error_list:
                            form.add_error(field, error)
                else:
                    form.add_error(None, e.messages) 
        else:
            messages.error(request,f'Errors:{form.errors.as_text()}')
            return redirect('indvi_models', model_name=model_name)
    else:
        form = DynamicForm(instance=instance)
        show_modal = False

    context = {
        "model_name": model_name,
        "form": form,
        "fields": fields_name_to_show,
        "rows": [row[0:-1] for row in page_obj],   # only this page; [0:-1] still removes the User entry
        "page_obj": page_obj,                      # turns on the Next/Previous bar and total count
        "show_modal": show_modal,
        "is_editing": bool(instance),
    }
    template_name, context = get_model_render_config(model_name, context, request.user)
    return render(request, template_name, context=context)

@login_required
@require_POST
def GeneralModelUpdateView(request, model_name, id):
    # Dynamically load model
    try:
        MyModel = apps.get_model(app_label='applications', model_name=model_name)
    except LookupError:
        messages.error(request, f"Error: Model '{model_name}' does not exist.")
        return redirect("index")
    
    DynamicForm = forms.modelform_factory(MyModel, fields='__all__', formfield_callback=html5_input_callback)
    
    fields_name_to_show = [field.verbose_name for field in MyModel._meta.fields]
    if 'User' in fields_name_to_show:
        fields_name_to_show.remove('User')

    instance = get_object_or_404(MyModel, pk=id, User=request.user)
    form = DynamicForm(request.POST, request.FILES, instance=instance)
    if form.is_valid():
        if MyModel.objects.filter(pk=form.data['item_id'],User=request.user).exists():
            if MyModel.objects.filter(**form.clean(),User=request.user).exists():
                messages.error(request,f'Errors: Same Entry exists!')
            else:
                updated_instance = form.save(commit=False)
                updated_instance.User = request.user
                updated_instance.save()
                form.save_m2m()
                messages.success(request, "Record updated successfully.")
        else:
            messages.error(request,"Invalid request!")
                
        return redirect('indvi_models', model_name=model_name)
    else:
        messages.error(request,f'Errors:{form.errors.as_text()}')
    
    context = {
        "model_name": model_name,
        "form": form,
        "fields": fields_name_to_show,
        "show_modal": True,      # Re-opens modal automatically on error
        "is_editing": True,      # Signals edit state to frontend JS
    }

    template_name, context = get_model_render_config(model_name, context, request.user)
    return render(request, template_name, context=context)

@login_required
@require_POST
def GeneralModelDeleteView(request, model_name, id):
# Dynamically load model
    try:
        MyModel = apps.get_model(app_label='applications', model_name=model_name)
    except LookupError:
        messages.error(request, f"Error: Model '{model_name}' does not exist.")
        return redirect("index")

    # Safely check if the record exists and belongs to the user
    instance = MyModel.objects.filter(id=id, User=request.user).first()
    
    if not instance:
        messages.error(request, "Record does not exist or you don't have permission to delete it.")
        return redirect('indvi_models', model_name=model_name)

    instance.delete()
    messages.success(request, "Record deleted successfully.")
    return redirect('indvi_models', model_name=model_name)