from django.db import models

# Create your models here.
class News(models.Model):
   url = models.CharField(max_length=100)


class UrlList(models.Model):
    url = models.CharField(max_length=100)
    talent = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'url_list'

class IgnoreStation2(models.Model):
    station = models.CharField(max_length=50)

    class Meta:
        managed = False
        db_table = 'ignore_station2'

class TvScrape(models.Model):
    url = models.CharField(max_length=100)
    talent = models.CharField(max_length=50)
    date = models.DateField()
    time = models.CharField(max_length=25)
    station = models.CharField(max_length=50)
    program_name = models.CharField(max_length=150)

    class Meta:
        managed = False
        db_table = 'tv_scrape'