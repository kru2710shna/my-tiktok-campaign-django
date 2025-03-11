# marketing/cron.py
from .models import TikTokCampaign
from .tiktok_api import TikTokAPIClient
import os

TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN", "YOUR_ACCESS_TOKEN")
ADVERTISER_ID = os.getenv("TIKTOK_ADVERTISER_ID", "YOUR_ADVERTISER_ID")

def check_and_update_campaigns():
    # Example: check campaigns in DB and automatically enable them
    campaigns = TikTokCampaign.objects.filter(status='INACTIVE')
    client = TikTokAPIClient(TIKTOK_ACCESS_TOKEN)
    for c in campaigns:
        if c.campaign_id:
            client.change_campaign_status(ADVERTISER_ID, c.campaign_id, "ENABLE")
            c.status = 'ACTIVE'
            c.save()
