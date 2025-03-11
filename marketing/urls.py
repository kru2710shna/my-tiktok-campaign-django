from django.urls import path
from .views import (
    CreateCampaignView,
    UploadCreativeView,
    SetTargetingView,
    ScheduleCampaignView,
    CampaignReportView
)

urlpatterns = [
    path('create_campaign/', CreateCampaignView.as_view(), name='create_campaign'),
    path('upload_creative/', UploadCreativeView.as_view(), name='upload_creative'),
    path('set_targeting/', SetTargetingView.as_view(), name='set_targeting'),
    path('schedule_campaign/', ScheduleCampaignView.as_view(), name='schedule_campaign'),
    path('report/', CampaignReportView.as_view(), name='campaign_report'),
]
