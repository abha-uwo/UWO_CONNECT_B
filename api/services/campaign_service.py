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
            
            channel = getattr(campaign, 'channel', 'WHATSAPP')
            
            if channel == 'WHATSAPP':
                token = client.whatsapp_access_token
                if not template or not token or not client.whatsapp_phone_number_id:
                    campaign.status = 'FAILED'
                    campaign.save()
                    return
            elif channel in ['FACEBOOK', 'INSTAGRAM']:
                body = getattr(campaign, 'body', '')
                fb_token = client.facebook_config.get('access_token') if channel == 'FACEBOOK' else client.instagram_config.get('access_token')
                page_id = client.facebook_config.get('page_id') if channel == 'FACEBOOK' else client.instagram_config.get('ig_id')
                if not body or not fb_token or not page_id:
                    campaign.status = 'FAILED'
                    campaign.save()
                    return
            else:
                campaign.status = 'FAILED'
                campaign.save()
                return

            # Determine audience
            if campaign.audience_filter == 'ALL':
                contacts = ContactRepository.filter_contacts(client=client)
            else:
                contacts = ContactRepository.filter_contacts(client=client, stage=campaign.audience_filter)

            for contact in contacts:
                try:
                    from ..integrations.meta_integration import MetaIntegration
                    if channel == 'WHATSAPP':
                        if not contact.phone_number:
                            campaign.total_failed += 1
                            continue
                        
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
                        res = MetaIntegration.send_whatsapp_message(client.whatsapp_phone_number_id, token, payload)
                        if res.status_code == 200:
                            campaign.total_sent += 1
                        else:
                            campaign.total_failed += 1
                    
                    elif channel in ['FACEBOOK', 'INSTAGRAM']:
                        if not contact.email and not contact.phone_number: # Need some ID, ideally PSID/IGSID stored in contact metadata
                            campaign.total_failed += 1
                            continue
                            
                        # Assuming contact.metadata contains 'psid' for FB or 'igsid' for IG
                        recipient_id = contact.metadata.get('psid') if channel == 'FACEBOOK' else contact.metadata.get('igsid')
                        if not recipient_id:
                            campaign.total_failed += 1
                            continue
                            
                        payload = {
                            "recipient": {"id": recipient_id},
                            "message": {"text": getattr(campaign, 'body', '')},
                            "messaging_type": "MESSAGE_TAG",
                            "tag": "POST_PURCHASE_UPDATE" # Safe tag for outside 24h window if applicable, otherwise might fail
                        }
                        url = f"https://graph.facebook.com/v19.0/{page_id}/messages"
                        res = requests.post(url, headers={"Authorization": f"Bearer {fb_token}"}, json=payload)
                        
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
