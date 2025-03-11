from django.db import models

# Create your models here.

class TikTokCampaign(models.Model):
    campaign_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    name= models.CharField(max_length=255)
    objective= models.CharField(max_length=100, default='REACH')
    status= models.CharField(max_length=50, default='INACTIVE')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.name
    


class TikTokCreative(models.Model):
    creative_id = models.CharField(max_length=255, unique=True, blank=True, null=True)
    campaign = models.ForeignKey(TikTokCampaign, on_delete=models.CASCADE, related_name='creatives')
    creative_type = models.CharField(max_length=50, default='IMAGE')  # 'IMAGE' or 'VIDEO'
    file_url = models.URLField(blank=True, null=True, help_text="URL of the uploaded creative on TikTok")
    local_file_path = models.CharField(max_length=500, blank=True, null=True, help_text="Local path before upload")

    def __str__(self):
        return f"{self.campaign.name} - {self.creative_type}"
    
    
    
    
    