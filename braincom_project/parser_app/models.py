from django.db import models
from django.contrib.postgres.fields import ArrayField

class MobileGadget(models.Model):
    full_name = models.CharField(max_length=255, db_index=True, null=True)                 
    color = models.CharField(max_length=255, db_index=True, null=True)                                     
    memory_volume = models.CharField(max_length=255, db_index=True, null=True)              
    price_use = models.CharField(max_length=255, db_index=True, null=True)                  
    price_action = models.CharField(max_length=255, db_index=True, null=True)              
    pic_links = ArrayField(models.URLField(), blank=True, default=list, null=True)        
    product_code = models.CharField(max_length=255, db_index=True, null=True)               
    review_count = models.IntegerField(blank=True, null=True, db_index=True)    
    series = models.CharField(max_length=255, db_index=True, null=True)                     
    display_size = models.CharField(max_length=255, db_index=True, null=True)                      
    resolution = models.CharField(max_length=255, db_index=True, null=True)          
    specifications = models.JSONField(null=True, blank=True)
                           

    def __str__(self):
        return f"Name: {self.full_name}."                                       

    class Meta: 
       verbose_name = "MobileGadget"