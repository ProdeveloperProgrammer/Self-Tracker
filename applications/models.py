from django.db import models, transaction,IntegrityError
from django.core.validators import *
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

# Create your models here.

#Please create user in all as of same type below with each field with thier verbose_name
class Certificate(models.Model):
    Title = models.CharField(blank=False,max_length=120,name='Title',verbose_name='Title')
    Provider = models.CharField(blank=False,max_length=120,name='Provider',verbose_name='Provider')
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

    def delete(self, *args, **kwargs):
        # Delete the file from storage when the model instance is deleted
        if self.Proof:
            self.Proof.delete(save=False)
        super().delete(*args, **kwargs)    

    def __str__(self):
        return f'{self.Title} by {self.Provider}'

    class Meta:
        verbose_name = "Certificate"

class MovieAndSeries(models.Model):
    Name = models.CharField(blank=False,max_length=120,name='Name',verbose_name='Name')
    Status = models.CharField(blank=False,max_length=120,choices={'Plan to watch':'Plan to watch','watching':'watching','completed':'completed'},name='Status',verbose_name='Status')
    Content_type = models.CharField(blank=False,max_length=120,choices={'movie':'movie','show':'show'},name='Content_type',verbose_name='Content Type')
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
        return f'On {self.Date} - {self.One_word_to_describe_the_day} By {self.User}' 
    
    class Meta:
        verbose_name_plural = "Daily Journels"

class SiteDiscovery(models.Model):
  Title = models.CharField(max_length=200, blank=False, verbose_name="Site Name")
  Site_url = models.URLField(max_length=1000, blank=False, verbose_name="Site URL")
  description = models.TextField(blank=True, verbose_name="Description")
  discovered_on = models.DateField(default=timezone.localdate,validators=[MaxValueValidator(timezone.localdate)],verbose_name="Discovered On",)
  User = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="User", editable=False)

  def __str__(self):
    return f"{self.Title} --> for {self.description[0:50]}..."

  def clean(self):
    super().clean()
    # Check if a record with the same User and Site_url already exists (excluding current object if updating)
    if self.User_id and self.Site_url:
      query = SiteDiscovery.objects.filter(User=self.User, Site_url=self.Site_url)
      if self.pk:
        query = query.exclude(pk=self.pk)

      if query.exists():
        raise ValidationError({"Site_url": "You have already added this Site URL."})

  def save(self, *args, **kwargs):
        # Run clean() to catch validation errors beforehand
        # self.clean()
        self.full_clean()
        
        try:
            # Wrap in an atomic savepoint to prevent breaking the transaction if a DB collision occurs
            with transaction.atomic():
                super().save(*args, **kwargs)
        except IntegrityError:
            raise ValidationError()

  class Meta:
    verbose_name_plural = "Sites Discovery"
    constraints = [
        models.UniqueConstraint(
            fields=["User", "Site_url"], name="unique_user_site_url"
        )
    ]