from django.db import models
from django.core.validators import *
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

#Please create user in all as of same type below with each field with thier verbose_name
class Certificate(models.Model):
    Title = models.CharField(blank=False,name='Title',verbose_name='Title')
    Provider = models.CharField(blank=False,name='Provider',verbose_name='Provider')
    Date = models.DateField(blank=False,default=timezone.localdate,validators=[MaxValueValidator(timezone.localdate)],name='date_recieved',verbose_name="Date Recieved")
    Proof = models.FileField(upload_to="certificate/",name='Proof',verbose_name='Proof')
    User = models.ForeignKey(User,on_delete=models.CASCADE,verbose_name='User',editable=False)

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
    User = models.ForeignKey(User,on_delete=models.CASCADE,verbose_name='User',editable=False)

    def __str__(self):
       return self.Name 
    
    class Meta:
        verbose_name_plural = "Movies and Series"

class DailyJournel(models.Model):
    Date = models.DateField(default=timezone.localdate,validators=[MaxValueValidator(timezone.localdate)],verbose_name='Date')
    Time = models.TimeField(default=timezone.localtime,verbose_name='Time')
    One_word_to_describe_the_day = models.CharField(blank=False, max_length=50,verbose_name="One word to describe the day")
    Journel = models.TextField(blank=False,verbose_name='Journel')
    User = models.ForeignKey(User,on_delete=models.CASCADE,verbose_name='User',editable=False)
    def __str__(self):
        return self.Date 
    
    class Meta:
        verbose_name_plural = "Daily Journels"

class SiteDiscovery(models.Model):
    Title = models.CharField(max_length=200,blank=False,verbose_name='Site Name')
    Site_url = models.URLField(max_length=1000,blank=False, unique=True,verbose_name='Site URL')
    description = models.TextField(blank=True,verbose_name='Description')
    discovered_on = models.DateField(default=timezone.localdate,validators=[MaxValueValidator(timezone.localdate)],verbose_name='Discovered On')
    User = models.ForeignKey(User,on_delete=models.CASCADE,verbose_name='User',editable=False)

    def __str__(self):
        return self.Title 
    
    class Meta:
        verbose_name_plural = "Sites Discovery"
    