import requests
from ..models import Campaign, Contact
from ..repositories.campaign_repository import CampaignRepository
from ..repositories.contact_repository import ContactRepository

class CampaignService:
    @staticmethod
    def process_campaign(campaign_id):
        try:
            campaign = CampaignRepository.get_campaign(id=campaign_id)
            client = campaign.client
            template = campaign.template
            
            token = client.whatsapp_access_token
            if not template or not token or not client.whatsapp_phone_number_id:
                campaign.status = 'FAILED'
                campaign.save()
                return

            # Determine audience
            if campaign.audience_filter == 'ALL':
                contacts = ContactRepository.filter_contacts(client=client)
            else:
                contacts = ContactRepository.filter_contacts(client=client, stage=campaign.audience_filter)

            url = f"https://graph.facebook.com/v19.0/{client.whatsapp_phone_number_id}/messages"
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }

            for contact in contacts:
                if not contact.phone_number:
                    campaign.total_failed += 1
                    continue
                
                # We need country code, assume it's in phone_number for now
                payload = {
                    "messaging_product": "whatsapp",
                    "to": contact.phone_number,
                    "type": "template",
                    "template": {
                        "name": template.name,
                        "language": {
                            "code": template.language
                        }
                    }
                }
                
                try:
                    from ..integrations.meta_integration import MetaIntegration
                    res = MetaIntegration.send_whatsapp_message(client.whatsapp_phone_number_id, token, payload)
                    if res.status_code == 200:
                        campaign.total_sent += 1
                    else:
                        campaign.total_failed += 1
                except Exception as e:
                    campaign.total_failed += 1

                # Update progress periodically or at the end
                campaign.save()
                
            campaign.status = 'COMPLETED'
            campaign.save()
        except Exception as e:
            print(f"Error processing campaign: {str(e)}")
            try:
                campaign = CampaignRepository.get_campaign(id=campaign_id)
                campaign.status = 'FAILED'
                campaign.save()
            except Campaign.DoesNotExist:
                pass
