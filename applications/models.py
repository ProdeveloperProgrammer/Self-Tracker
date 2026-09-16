from django.db import models
from django.core.validators import *
from django.utils import timezone
import uuid

# Create your models here.
class Certificate(models.Model):
    Title = models.CharField(blank=False,name='Title',verbose_name='Title')
    Provider = models.CharField(blank=False,name='Provider',verbose_name='Provider')
    Date = models.DateField(blank=False,default=timezone.localdate(),validators=[MaxValueValidator(timezone.localdate())],name='date_recieved',verbose_name="Date Recieved")
    Proof = models.FileField(upload_to="certificate/",name='Proof',verbose_name='Proof')

    def save(self, *args, **kwargs):
    # Check if the instance already exists in the database (an update, not a creation)
        if self.pk:
          try:
            old_file = Certificate.objects.get(pk=self.pk).Proof
            # If a new file is provided and it differs from the old one, delete the old file
            if old_file and old_file != self.Proof:
              old_file.delete(save=False)
          except Certificate.DoesNotExist:
            pass
        super().save(*args, **kwargs) 

    def delete(self):
        # Delete the file from storage when the model instance is deleted
        if self.Proof:
            self.Proof.delete(save=False)
            super().delete()    

    def __str__(self):
        return f'{self.Title} by {self.Provider}'

    class Meta:
        verbose_name = "Certificate"

class MovieAndSeries(models.Model):
    Name = models.CharField(blank=False,name='Name',verbose_name='Name')
    Status = models.CharField(blank=False,choices={'Plan to watch':'Plan to watch','watching':'watching','completed':'completed'},name='Status',verbose_name='Status')
    Content_type = models.CharField(blank=False,choices={'movie':'movie','show':'show'},name='Content_type',verbose_name='Content Type')
    Anime = models.BooleanField(name='Anime',verbose_name='Anime')
    Note = models.TextField(blank=True,name='Note',verbose_name='Note')

    def __str__(self):
       return self.Name 
    
    class Meta:
        verbose_name_plural = "Movies and Series"
   