import os
import json
import requests
from django.http import HttpResponse
from ..models import Client, Contact, Message, Automation, KnowledgeChunk
from .ai_service import get_ai_response, get_rag_response, get_embedding, find_relevant_chunks
from ..repositories.client_repository import ClientRepository
from ..repositories.contact_repository import ContactRepository
from ..repositories.message_repository import MessageRepository
from ..repositories.automation_repository import AutomationRepository
from ..repositories.knowledge_repository import KnowledgeRepository
import logging
logger = logging.getLogger(__name__)

class MetaWebhookService:
    @staticmethod
    def verify_whatsapp_webhook(mode, token, challenge):
        verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN', 'aisaconnect_secure_token')
        if mode and token:
            if mode == 'subscribe' and token == verify_token:
                print("WEBHOOK_VERIFIED")
                return HttpResponse(challenge, content_type="text/plain", status=200)
            else:
                return HttpResponse("Forbidden", content_type="text/plain", status=403)
        return HttpResponse("Bad Request", content_type="text/plain", status=400)

    @staticmethod
    def verify_fb_ig_webhook(mode, token, challenge):
        verify_token = os.getenv('WHATSAPP_VERIFY_TOKEN') or 'aisaconnect_secure_token'
        if mode and token:
            if mode == 'subscribe' and token == verify_token:
                print("FB/IG WEBHOOK_VERIFIED")
                return HttpResponse(challenge, content_type="text/plain", status=200)
            else:
                return HttpResponse("Forbidden", content_type="text/plain", status=403)
        return HttpResponse("Bad Request", content_type="text/plain", status=400)

    @staticmethod
    def handle_whatsapp_message(data):
        print("Incoming WhatsApp Webhook Payload:", json.dumps(data, indent=2))
        try:
            if data.get('object') == 'whatsapp_business_account':
                for entry in data.get('entry') or []:
                    entry = entry or {}
                    for change in entry.get('changes') or []:
                        change = change or {}
                        value = change.get('value') or {}
                        metadata = value.get('metadata') or {}
                        phone_number_id = metadata.get('phone_number_id')
                        
                        client = ClientRepository.filter_clients(whatsapp_phone_number_id=phone_number_id).first()
                        if not client:
                            print(f"No client found for phone_number_id: {phone_number_id}")
                            continue

                        if not client.automation_enabled:
                            print(f"Automation disabled for client: {client.business_name}")
                            continue

                        contacts = value.get('contacts') or []
                        contact_name = "Unknown"
                        if contacts:
                            contact_name = (contacts[0].get('profile') or {}).get('name', 'Unknown')

                        messages = value.get('messages') or []
                        for msg in messages:
                            from_number = msg.get('from')
                            msg_type = msg.get('type')
                            body = ""

                            if msg_type == 'text':
                                body = (msg.get('text') or {}).get('body', '')
                            elif msg_type == 'audio' or msg_type == 'voice':
                                audio_data = msg.get('audio') or msg.get('voice') or {}
                                audio_id = audio_data.get('id')
                                if audio_id and client.whatsapp_access_token:
                                    try:
                                        media_url_endpoint = f"https://graph.facebook.com/v18.0/{audio_id}"
                                        headers = {"Authorization": f"Bearer {client.whatsapp_access_token}"}
                                        media_res = requests.get(media_url_endpoint, headers=headers, timeout=5).json()
                                        media_url = media_res.get('url')
                                        if media_url:
                                            from ..utils.whisper_utils import transcribe_audio_with_whisper
                                            transcribed_text = transcribe_audio_with_whisper(media_url, client.whatsapp_access_token)
                                            if transcribed_text:
                                                body = transcribed_text
                                                print(f"Transcribed WhatsApp audio successfully: {body}")
                                    except Exception as ex:
                                        print(f"Failed parsing incoming voice note: {str(ex)}")
                            elif msg_type == 'button':
                                body = (msg.get('button') or {}).get('text', '')
                            elif msg_type == 'interactive':
                                i_type = (msg.get('interactive') or {}).get('type')
                                if i_type == 'button_reply':
                                    body = (msg.get('interactive') or {}).get('button_reply', {}).get('title', '')
                                elif i_type == 'list_reply':
                                    body = (msg.get('interactive') or {}).get('list_reply', {}).get('title', '')
                            
                            contact, _ = ContactRepository.get_contact_or_create(
                                client=client,
                                platform_id=from_number,
                                defaults={
                                    'phone_number': from_number,
                                    'name': contact_name,
                                    'stage': 'NEW'
                                }
                            )

                            MessageRepository.create_message(
                                client=client,
                                channel='WHATSAPP',
                                from_address=from_number,
                                to_address=phone_number_id,
                                body=body,
                                message_type='INCOMING',
                                whatsapp_message_id=msg.get('id'),
                                status='RECEIVED',
                                metadata=msg
                            )

                            if body:
                                if not contact.bot_paused:
                                    MetaWebhookService.handle_automations_whatsapp(client, from_number, body, phone_number_id)
                                else:
                                    print(f"Bot paused for contact {from_number}. No automated response.")
            return {"status": "success", "status_code": 200}
        except Exception as e:
            print(f"Error processing webhook: {str(e)}")
            return {"status": "error", "status_code": 500}

    @staticmethod
    def handle_fb_ig_message(data):
        logger.warning(f"Incoming FB/IG Webhook Payload: {json.dumps(data)}")
        try:
            for entry in data.get('entry') or []:
                entry = entry or {}
                recipient_id = entry.get('id')
                
                client = None
                platform = None
                
                if data.get('object') == 'page':
                    all_clients = ClientRepository.get_all_clients()
                    for c in all_clients:
                        fc = c.facebook_config or {}
                        if str(fc.get('page_id', '')) == str(recipient_id):
                            client = c
                            break
                    platform = 'FACEBOOK'
                elif data.get('object') == 'instagram':
                    all_clients = ClientRepository.get_all_clients()
                    for c in all_clients:
                        ic = c.instagram_config or {}
                        fc = c.facebook_config or {}
                        ig_id = str(ic.get('instagram_business_id', ''))
                        ig_page_id = str(ic.get('page_id', ''))
                        fb_page_id = str(fc.get('page_id', ''))
                        if str(recipient_id) in [ig_id, ig_page_id, fb_page_id] and (ig_id or ig_page_id or fb_page_id):
                            client = c
                            break
                    platform = 'INSTAGRAM'
                
                if not client:
                    logger.warning(f"No client found for {platform} recipient ID: {recipient_id}")
                    continue

                if not client.automation_enabled:
                    print(f"Automation disabled for client: {client.business_name}")
                    continue

                messaging = entry.get('messaging', [])
                for event in messaging:
                    sender_id = event.get('sender', {}).get('id')
                    body = ""
                    if 'message' in event:
                        msg_data = event.get('message', {})
                        if 'quick_reply' in msg_data:
                            body = msg_data.get('quick_reply', {}).get('payload', '')
                        else:
                            body = msg_data.get('text', '')
                    elif 'postback' in event:
                        body = event.get('postback', {}).get('payload', '') or event.get('postback', {}).get('title', '')
                    
                    if not body:
                        continue
                    
                    contact, _ = ContactRepository.get_contact_or_create(
                        client=client,
                        platform_id=sender_id,
                        defaults={
                            'phone_number': sender_id,
                            'name': f"{platform} User",
                            'stage': 'NEW'
                        }
                    )

                    MessageRepository.create_message(
                        client=client,
                        channel=platform,
                        from_address=sender_id,
                        to_address=recipient_id,
                        body=body,
                        message_type='INCOMING',
                        status='RECEIVED',
                        metadata=event
                    )

                    if body:
                        if not contact.bot_paused:
                            MetaWebhookService.handle_automations_fb_ig(client, platform, sender_id, body)
                        else:
                            print(f"Bot paused for {platform} contact {sender_id}. No automated response.")

            return {"status": "success", "status_code": 200}
        except Exception as e:
            logger.error(f"Error processing FB/IG webhook: {str(e)}")
            return {"status": "error", "status_code": 500}

    @staticmethod
    def handle_automations_whatsapp(client, to_number, incoming_text, phone_number_id):
        from .workflow_service import WorkflowEngine
        wf_messages = WorkflowEngine.process_workflow(client, to_number, incoming_text)
        if wf_messages:
            for msg in wf_messages:
                MetaWebhookService.send_whatsapp_message(
                    client=client,
                    to_number=to_number,
                    text_body=msg.get('body', ''),
                    phone_number_id=phone_number_id,
                    buttons=msg.get('buttons'),
                    media_url=msg.get('media_url'),
                    media_type=msg.get('type')
                )
            return

        automations = AutomationRepository.filter_automations(client=client, enabled=True, trigger_type='KEYWORD')
        incoming_text_lower = incoming_text.lower().strip()
        
        match_found = False
        for auto in automations:
            auto_channels = auto.channels or []
            if len(auto_channels) > 0 and 'WHATSAPP' not in auto_channels:
                continue

            if auto.keywords:
                for keyword in auto.keywords:
                    kw = keyword.lower().strip()
                    if kw and (kw == incoming_text_lower or kw in incoming_text_lower):
                        MetaWebhookService.send_whatsapp_message(client, to_number, auto.response, phone_number_id, auto.buttons)
                        match_found = True
                        break
            if match_found: break

        if not match_found and client.ai_enabled:
            chunks = KnowledgeRepository.filter_chunks(client=client).exclude(embedding=[])
            if chunks.exists():
                query_embedding = get_embedding(incoming_text)
                if query_embedding:
                    chunks_data = [{
                        'text': c.chunk_text,
                        'embedding': c.embedding,
                        'doc_title': c.document.title
                    } for c in chunks.select_related('document')]
                    relevant = find_relevant_chunks(query_embedding, chunks_data, top_k=5)
                    
                    if relevant and relevant[0]['score'] > 0.3:
                        ai_reply = get_rag_response(incoming_text, relevant)
                    else:
                        ai_reply = get_ai_response(incoming_text, client.ai_context or "")
                else:
                    ai_reply = get_ai_response(incoming_text, client.ai_context or "")
            else:
                ai_reply = get_ai_response(incoming_text, client.ai_context or "")

            if ai_reply:
                MetaWebhookService.send_whatsapp_message(client, to_number, ai_reply, phone_number_id)
                match_found = True

        if not match_found and client.greeting_enabled and client.greeting_message:
            MetaWebhookService.send_whatsapp_message(client, to_number, client.greeting_message, phone_number_id, client.greeting_buttons)

    @staticmethod
    def handle_automations_fb_ig(client, platform, sender_id, incoming_text):
        from .workflow_service import WorkflowEngine
        wf_messages = WorkflowEngine.process_workflow(client, sender_id, incoming_text, platform)
        if wf_messages:
            for msg in wf_messages:
                MetaWebhookService.send_fb_ig_message(
                    client=client,
                    platform=platform,
                    recipient_id=sender_id,
                    text_body=msg.get('body', ''),
                    buttons=msg.get('buttons'),
                    media_url=msg.get('media_url'),
                    media_type=msg.get('type')
                )
            return

        automations = AutomationRepository.filter_automations(client=client, enabled=True, trigger_type='KEYWORD')
        incoming_text_lower = incoming_text.lower().strip()
        
        match_found = False
        for auto in automations:
            auto_channels = auto.channels or []
            if len(auto_channels) > 0 and platform not in auto_channels:
                continue
            if len(auto_channels) == 0 and platform != 'WHATSAPP':
                continue

            if auto.keywords:
                for keyword in auto.keywords:
                    kw = keyword.lower().strip()
                    if kw and (kw == incoming_text_lower or kw in incoming_text_lower):
                        MetaWebhookService.send_fb_ig_message(client, platform, sender_id, auto.response, auto.buttons)
                        match_found = True
                        break
            if match_found: break

        if not match_found and client.ai_enabled:
            ai_reply = None
            chunks = KnowledgeRepository.filter_chunks(client=client).exclude(embedding=[])
            if chunks.exists():
                query_embedding = get_embedding(incoming_text)
                if query_embedding:
                    chunks_data = [{
                        'text': c.chunk_text,
                        'embedding': c.embedding,
                        'doc_title': c.document.title
                    } for c in chunks.select_related('document')]
                    relevant = find_relevant_chunks(query_embedding, chunks_data, top_k=5)
                    if relevant and relevant[0]['score'] > 0.3:
                        ai_reply = get_rag_response(incoming_text, relevant)
            
            if not ai_reply:
                ai_reply = get_ai_response(incoming_text, client.ai_context or "")
                
            if ai_reply:
                MetaWebhookService.send_fb_ig_message(client, platform, sender_id, ai_reply)
                match_found = True

        if not match_found and client.greeting_enabled and client.greeting_message:
            MetaWebhookService.send_fb_ig_message(client, platform, sender_id, client.greeting_message, client.greeting_buttons)

    @staticmethod
    def send_whatsapp_message(client, to_number, text_body, phone_number_id, buttons=None, media_url=None, media_type=None):
        url = f"https://graph.facebook.com/{os.getenv('WHATSAPP_API_VERSION', 'v19.0')}/{phone_number_id}/messages"
        token = client.whatsapp_access_token
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        if media_url:
            m_type = media_type
            if not m_type:
                m_type = 'video' if any(ext in media_url.lower() for ext in ['.mp4', '.mov', '.avi']) else 'image'
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": m_type,
                m_type: {
                    "link": media_url
                }
            }
            if text_body:
                payload[m_type]["caption"] = text_body
        elif buttons and len(buttons) > 0:
            buttons_payload = []
            for i, btn_text in enumerate(buttons[:3]):
                buttons_payload.append({
                    "type": "reply",
                    "reply": {
                        "id": f"btn_{i}",
                        "title": btn_text[:20]
                    }
                })
            
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": text_body or "Select an option:"},
                    "action": {"buttons": buttons_payload}
                }
            }
        else:
            payload = {
                "messaging_product": "whatsapp",
                "to": to_number,
                "type": "text",
                "text": {"body": text_body}
            }

        try:
            response = requests.post(url, headers=headers, json=payload)
            res_data = response.json()
            print(f"WhatsApp API Response: {res_data}")

            MessageRepository.create_message(
                client=client,
                channel='WHATSAPP',
                from_address=phone_number_id,
                to_address=to_number,
                body=text_body or f"[{media_type or 'Media'} Message]",
                message_type='OUTGOING',
                whatsapp_message_id=res_data.get('messages', [{}])[0].get('id') if 'messages' in res_data else None,
                status='SENT' if response.status_code == 200 else 'FAILED',
                metadata={"payload": payload, "response": res_data}
            )
        except Exception as e:
            print(f"Failed to send message: {str(e)}")

    @staticmethod
    def send_fb_ig_message(client, platform, recipient_id, text_body, buttons=None, media_url=None, media_type=None):
        config = client.facebook_config if platform == 'FACEBOOK' else (client.instagram_config or {})
        access_token = config.get('access_token') or (client.facebook_config or {}).get('access_token') or client.whatsapp_access_token
        
        if not access_token:
            print(f"No access token found for {platform} messaging")
            return
            
        if platform == 'INSTAGRAM':
            ig_id = (client.instagram_config or {}).get('instagram_business_id') or 'me'
            url = f"https://graph.facebook.com/v20.0/{ig_id}/messages"
        else:
            url = "https://graph.facebook.com/v20.0/me/messages"

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        message_payload = {}
        if media_url:
            m_type = media_type or 'image'
            if not media_type:
                m_type = 'video' if any(ext in media_url.lower() for ext in ['.mp4', '.mov', '.avi']) else 'image'
            message_payload = {
                "attachment": {
                    "type": m_type,
                    "payload": {
                        "url": media_url,
                        "is_reusable": True
                    }
                }
            }
        elif buttons and len(buttons) > 0:
            quick_replies = []
            for btn in buttons[:13]:
                quick_replies.append({
                    "content_type": "text",
                    "title": btn[:20],
                    "payload": btn
                })
            message_payload = {
                "text": text_body or "Please choose an option:",
                "quick_replies": quick_replies
            }
        else:
            message_payload = {
                "text": text_body
            }
            
        payload = {
            "recipient": {"id": recipient_id},
            "message": message_payload
        }
        
        try:
            res = requests.post(url, json=payload, headers=headers)
            print(f"{platform} Send Response:", res.status_code, res.text)
            if res.status_code != 200:
                fallback_url = "https://graph.facebook.com/v20.0/me/messages"
                res_fb = requests.post(fallback_url, json=payload, headers=headers)
                print(f"{platform} Fallback Send Response:", res_fb.status_code, res_fb.text)
            
            MessageRepository.create_message(
                client=client,
                channel=platform,
                from_address='SYSTEM',
                to_address=recipient_id,
                body=text_body or f"[{media_type or 'Attachment'}]",
                message_type='OUTGOING',
                status='SENT'
            )
        except Exception as e:
            print(f"Failed to send {platform} message:", str(e))
