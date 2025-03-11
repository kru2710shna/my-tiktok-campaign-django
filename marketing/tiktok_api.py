import requests
import logging

logger = logging.getLogger(__name__)

class TikTokAPIClient:
    """
    A simple client to handle TikTok API requests.
    """
    BASE_URL = "https://business-api.tiktok.com/open_api/v1.3/"

    def __init__(self, access_token):
        self.access_token = access_token

    def create_campaign(self, advertiser_id, campaign_data):
        """
        Example: Creates a campaign on TikTok.
        """
        url = f"{self.BASE_URL}campaign/create/"
        headers = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
        payload = {
            "advertiser_id": advertiser_id,
            "campaign_name": campaign_data["name"],
            "objective_type": campaign_data["objective"],
            "budget_mode": "BUDGET_MODE_INFINITE",  # example
            "budget": 0  # example
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()

    def upload_creative(self, advertiser_id, creative_type, file_path_or_url):
        """
        Example: Upload a creative (image/video) to TikTok. 
        In reality, you may have to upload in multiple steps for videos, or sign upload parameters, etc.
        """
        url = f"{self.BASE_URL}file/upload/"
        headers = {
            "Access-Token": self.access_token,
        }
        files = {
            'file': open(file_path_or_url, 'rb')  # For demonstration if we have a local file
        }
        data = {
            "advertiser_id": advertiser_id,
            "upload_type": "UPLOAD_TYPE_IMAGE" if creative_type == "IMAGE" else "UPLOAD_TYPE_VIDEO"
        }
        response = requests.post(url, headers=headers, files=files, data=data)
        return response.json()

    def set_targeting(self, advertiser_id, campaign_id, targeting_params):
        """
        Example: Set targeting for an existing campaign.
        """
        url = f"{self.BASE_URL}targeting/update/"
        headers = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
        payload = {
            "advertiser_id": advertiser_id,
            "campaign_id": campaign_id,
            "targeting_list": targeting_params
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()

    def change_campaign_status(self, advertiser_id, campaign_id, status):
        """
        Example: Start/Stop campaign.
        """
        url = f"{self.BASE_URL}campaign/update/status/"
        headers = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
        payload = {
            "advertiser_id": advertiser_id,
            "campaign_ids": [campaign_id],
            "operation_status": status  # e.g., "ENABLE" or "DISABLE"
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()

    def get_reports(self, advertiser_id, campaign_id):
        """
        Example: Extract campaign-level reports.
        """
        url = f"{self.BASE_URL}report/integrated/get/"
        headers = {
            "Access-Token": self.access_token,
            "Content-Type": "application/json"
        }
        payload = {
            "advertiser_id": advertiser_id,
            "service_type": "AUCTION",
            "data_level": "CAMPAIGN",
            "dimensions": ["campaign_id"],
            "metrics": ["spend", "impressions", "clicks"],
            "filters": [
                {
                    "field_name": "campaign_id",
                    "filter_type": "IN",
                    "field_value": [campaign_id]
                }
            ]
        }
        response = requests.post(url, json=payload, headers=headers)
        return response.json()

