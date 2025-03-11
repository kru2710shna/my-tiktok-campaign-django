import os
from django.http import JsonResponse
from django.views import View
from .models import TikTokCampaign, TikTokCreative
from .tiktok_api import TikTokAPIClient

# Assume you store these in environment variables or your secrets manager
TIKTOK_ACCESS_TOKEN = os.getenv("TIKTOK_ACCESS_TOKEN", "YOUR_ACCESS_TOKEN")
ADVERTISER_ID = os.getenv("TIKTOK_ADVERTISER_ID", "YOUR_ADVERTISER_ID")

class CreateCampaignView(View):
    def post(self, request):
        """
        Expected JSON structure:
        {
            "name": "My Campaign",
            "objective": "REACH"  # or "TRAFFIC", "CONVERSION", etc.
        }
        """
        import json
        data = json.loads(request.body)
        name = data.get("name")
        objective = data.get("objective", "REACH")

        # Step 1: Create local DB record
        campaign = TikTokCampaign.objects.create(name=name, objective=objective)

        # Step 2: Call TikTok API
        client = TikTokAPIClient(TIKTOK_ACCESS_TOKEN)
        campaign_data = {
            "name": name,
            "objective": objective
        }
        api_response = client.create_campaign(ADVERTISER_ID, campaign_data)

        # You need to parse the response according to TikTok's actual JSON structure
        if api_response.get("code") == 0:
            # Example: extracting the 'campaign_id' from a successful response
            tiktok_campaign_id = api_response["data"].get("campaign_id")
            campaign.campaign_id = tiktok_campaign_id
            campaign.status = "ACTIVE"  # or whatever status
            campaign.save()
            return JsonResponse({"message": "Campaign created", "campaign_id": tiktok_campaign_id})
        else:
            return JsonResponse({"error": "Failed to create campaign", "details": api_response}, status=400)


class UploadCreativeView(View):
    def post(self, request):
        """
        Expected JSON structure:
        {
            "campaign_id": "<local DB id or tiktok campaign_id>",
            "creative_type": "IMAGE" or "VIDEO",
            "file_path": "/path/to/file"  # local server file path
        }
        """
        import json
        data = json.loads(request.body)
        local_campaign_id = data.get("campaign_id")
        creative_type = data.get("creative_type", "IMAGE")
        file_path = data.get("file_path")

        # Retrieve the campaign from DB
        try:
            campaign = TikTokCampaign.objects.get(id=local_campaign_id)
        except TikTokCampaign.DoesNotExist:
            return JsonResponse({"error": "Campaign not found"}, status=404)

        # Upload the creative to TikTok
        client = TikTokAPIClient(TIKTOK_ACCESS_TOKEN)
        response = client.upload_creative(ADVERTISER_ID, creative_type, file_path)

        if response.get("code") == 0:
            # Suppose the returned creative_id is in response["data"]["creative_id"]
            creative_id = response["data"].get("creative_id")
            file_url = response["data"].get("file_url")

            # Store it in DB
            creative = TikTokCreative.objects.create(
                campaign=campaign,
                creative_id=creative_id,
                creative_type=creative_type,
                file_url=file_url,
                local_file_path=file_path
            )
            return JsonResponse({"message": "Creative uploaded", "creative_id": creative_id})
        else:
            return JsonResponse({"error": "Failed to upload creative", "details": response}, status=400)


class SetTargetingView(View):
    def post(self, request):
        """
        Example JSON structure:
        {
            "campaign_id": <local db pk or tiktok campaign id>,
            "targeting_params": {
                "age": [18, 25],
                "gender": "male",
                ...
            }
        }
        """
        import json
        data = json.loads(request.body)
        local_campaign_id = data.get("campaign_id")
        targeting_params = data.get("targeting_params", {})

        # Retrieve local campaign
        try:
            campaign = TikTokCampaign.objects.get(id=local_campaign_id)
        except TikTokCampaign.DoesNotExist:
            return JsonResponse({"error": "Campaign not found"}, status=404)

        if not campaign.campaign_id:
            return JsonResponse({"error": "No TikTok campaign_id associated with this campaign"}, status=400)

        client = TikTokAPIClient(TIKTOK_ACCESS_TOKEN)
        response = client.set_targeting(ADVERTISER_ID, campaign.campaign_id, targeting_params)

        if response.get("code") == 0:
            return JsonResponse({"message": "Targeting updated successfully"})
        else:
            return JsonResponse({"error": "Failed to update targeting", "details": response}, status=400)


class ScheduleCampaignView(View):
    """
    In a real scenario, you'd do something more robust.
    For demonstration, we'll assume we "schedule" by simply enabling/disabling the campaign now.
    """
    def post(self, request):
        """
        Example JSON structure:
        {
            "campaign_id": <local db pk>,
            "action": "START" or "STOP"
        }
        """
        import json
        data = json.loads(request.body)
        local_campaign_id = data.get("campaign_id")
        action = data.get("action")

        try:
            campaign = TikTokCampaign.objects.get(id=local_campaign_id)
        except TikTokCampaign.DoesNotExist:
            return JsonResponse({"error": "Campaign not found"}, status=404)

        if not campaign.campaign_id:
            return JsonResponse({"error": "No TikTok campaign_id associated with this campaign"}, status=400)

        client = TikTokAPIClient(TIKTOK_ACCESS_TOKEN)
        status = "ENABLE" if action == "START" else "DISABLE"
        response = client.change_campaign_status(ADVERTISER_ID, campaign.campaign_id, status)

        if response.get("code") == 0:
            # update local campaign status
            campaign.status = "ACTIVE" if action == "START" else "INACTIVE"
            campaign.save()
            return JsonResponse({"message": f"Campaign {action}ed successfully"})
        else:
            return JsonResponse({"error": "Failed to change campaign status", "details": response}, status=400)


class CampaignReportView(View):
    """
    Fetch a simple campaign report from TikTok.
    """
    def get(self, request):
        """
        We can pass ?campaign_id=<local db pk> in query params.
        """
        local_campaign_id = request.GET.get("campaign_id")
        if not local_campaign_id:
            return JsonResponse({"error": "campaign_id query param required"}, status=400)

        try:
            campaign = TikTokCampaign.objects.get(id=local_campaign_id)
        except TikTokCampaign.DoesNotExist:
            return JsonResponse({"error": "Campaign not found"}, status=404)

        if not campaign.campaign_id:
            return JsonResponse({"error": "No TikTok campaign_id associated with this campaign"}, status=400)

        client = TikTokAPIClient(TIKTOK_ACCESS_TOKEN)
        response = client.get_reports(ADVERTISER_ID, campaign.campaign_id)

        if response.get("code") == 0:
            data = response.get("data", {})
            return JsonResponse({"report_data": data})
        else:
            return JsonResponse({"error": "Failed to get report", "details": response}, status=400)
