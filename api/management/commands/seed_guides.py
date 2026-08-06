from django.core.management.base import BaseCommand
from api.models import Guide, GuideSection, GuideStep

class Command(BaseCommand):
    help = 'Seeds complete, interactive learning center guides for all UWOConnect modules.'

    def handle(self, *args, **options):
        self.stdout.write('Seeding UWOConnect Interactive Learning Center Guides...')

        GUIDES_DATA = [
            # ─────────────────────────────────────────────────────────────────
            # 1. CONNECTORS GUIDE
            # ─────────────────────────────────────────────────────────────────
            {
                'slug': 'connectors',
                'title': 'Connectors & Integrations Master Guide',
                'icon': 'Link2',
                'category': 'Integrations',
                'description': 'Complete step-by-step guide to linking WhatsApp API, Meta, Instagram, Telegram, Google Workspace, CRM, and AI providers with UWOConnect.',
                'estimated_time': '15 mins',
                'order': 1,
                'sections': [
                    {
                        'title': 'Overview & Architecture',
                        'icon': 'Info',
                        'steps': [
                            {
                                'title': 'What are Connectors?',
                                'step_type': 'text',
                                'content': 'Connectors act as secure authentication bridges connecting third-party platforms (WhatsApp Business API, Instagram, Meta, Telegram, Google Sheets, OpenAI, Gemini) directly into UWOConnect\'s automation core.'
                            },
                            {
                                'title': 'Why Connectors are Essential',
                                'step_type': 'tip',
                                'content': 'Without connectors, automations cannot send messages or retrieve external data. Connecting platforms allows unified inboxing, AI bot replies, automated lead capturing, and automated broadcast campaigns.'
                            },
                            {
                                'title': 'System Flow Diagram',
                                'step_type': 'diagram',
                                'content': 'External Customer Message ➔ Webhook Receiver ➔ UWOConnect Flow Engine ➔ AI / Connector Action ➔ Instant Reply Sent'
                            }
                        ]
                    },
                    {
                        'title': 'Available Connectors Matrix',
                        'icon': 'Grid',
                        'steps': [
                            {
                                'title': 'Supported Social & Messaging Platforms',
                                'step_type': 'checklist',
                                'checklist_items': [
                                    {'text': 'WhatsApp Business Cloud API (Official Meta)', 'checked': True},
                                    {'text': 'Instagram Direct Messages & Comments', 'checked': True},
                                    {'text': 'Facebook Messenger & Page Inbox', 'checked': True},
                                    {'text': 'Telegram Bot API (@BotFather)', 'checked': True},
                                    {'text': 'YouTube Comments & Channel Automation', 'checked': True},
                                    {'text': 'LinkedIn & X (Twitter) Webhooks', 'checked': True}
                                ]
                            },
                            {
                                'title': 'Supported Cloud & Productivity Services',
                                'step_type': 'checklist',
                                'checklist_items': [
                                    {'text': 'Google Sheets (Live Row Sync & Lead Export)', 'checked': True},
                                    {'text': 'Google Docs & Google Drive (Knowledge Base RAG)', 'checked': True},
                                    {'text': 'OneDrive & Microsoft Teams Integration', 'checked': True},
                                    {'text': 'Slack & Discord Event Webhooks', 'checked': True},
                                    {'text': 'Airtable, HubSpot & Salesforce CRM Sync', 'checked': True}
                                ]
                            }
                        ]
                    },
                    {
                        'title': 'Step-by-Step: WhatsApp Business API Setup',
                        'icon': 'Smartphone',
                        'steps': [
                            {
                                'title': 'Prerequisites Checklist',
                                'step_type': 'checklist',
                                'checklist_items': [
                                    {'text': 'Registered Meta Developer Account at developers.facebook.com', 'checked': False},
                                    {'text': 'Verified Meta Business Manager Profile', 'checked': False},
                                    {'text': 'Dedicated Phone Number (Not currently active on personal WhatsApp)', 'checked': False},
                                    {'text': 'Credit Card linked to Meta Billing (for messaging tier access)', 'checked': False}
                                ]
                            },
                            {
                                'title': 'Step 1: Create Meta Developer App',
                                'step_type': 'text',
                                'content': '1. Go to developers.facebook.com ➔ Click "My Apps" ➔ "Create App".\n2. Select "Other" ➔ Choose "Business" app type.\n3. Enter your App Name (e.g. UWOConnect WhatsApp) and link your Business Account.'
                            },
                            {
                                'title': 'Step 2: Add WhatsApp Product',
                                'step_type': 'text',
                                'content': 'In your App Dashboard, scroll down to "WhatsApp" and click "Set Up". Select your Business Manager profile from the dropdown.'
                            },
                            {
                                'title': 'Step 3: Generate Permanent System Access Token',
                                'step_type': 'code',
                                'code_language': 'bash',
                                'code_snippet': 'Go to Business Settings ➔ System Users ➔ Add System User (Admin role)\nClick "Add Assets" ➔ Select your App ➔ Enable whatsapp_business_messaging & whatsapp_business_management permissions\nClick "Generate Token" ➔ Copy token string',
                                'content': 'Copy the generated System Token. Do not use temporary 24-hour test tokens for production.'
                            },
                            {
                                'title': 'Step 4: Copy Phone Number ID & WABA ID',
                                'step_type': 'warning',
                                'content': 'Copy your Phone Number ID and WhatsApp Business Account ID (WABA ID) from Meta WhatsApp API Setup tab. Paste them into UWOConnect Channels ➔ Settings.'
                            },
                            {
                                'title': 'Step 5: Configure & Verify Webhook',
                                'step_type': 'code',
                                'code_language': 'json',
                                'code_snippet': 'Callback URL: https://api.uwoconnect.com/api/webhook/whatsapp/\nVerify Token: uwoconnect_secure_token\nSubscribed Fields: messages, message_template_status_update',
                                'content': 'Click "Verify and Save" in Meta Webhook config. Ensure status shows active green check.'
                            }
                        ]
                    },
                    {
                        'title': 'Troubleshooting & Common Errors',
                        'icon': 'AlertTriangle',
                        'steps': [
                            {
                                'title': 'Error 190: Access Token Expired',
                                'step_type': 'warning',
                                'content': 'Cause: You used a temporary user token instead of a System User Permanent Token. Fix: Generate a permanent token under Meta Business Settings ➔ System Users.'
                            },
                            {
                                'title': 'Error 100: Webhook Verification Failed',
                                'step_type': 'warning',
                                'content': 'Cause: Verify token string mismatch. Fix: Ensure the exact verify token (e.g. uwoconnect_secure_token) is entered in both Meta Dashboard and UWOConnect settings.'
                            }
                        ]
                    }
                ]
            },

            # ─────────────────────────────────────────────────────────────────
            # 2. BROADCASTS GUIDE
            # ─────────────────────────────────────────────────────────────────
            {
                'slug': 'broadcasts',
                'title': 'WhatsApp Broadcasts & Bulk Campaigns Guide',
                'icon': 'Megaphone',
                'category': 'Marketing',
                'description': 'Master high-converting bulk WhatsApp campaigns, Meta template approvals, variable personalization, and delivery analytics.',
                'estimated_time': '12 mins',
                'order': 2,
                'sections': [
                    {
                        'title': 'Campaign Overview & Best Practices',
                        'icon': 'Info',
                        'steps': [
                            {
                                'title': 'What are WhatsApp Broadcasts?',
                                'step_type': 'text',
                                'content': 'Broadcasts allow you to send Meta-approved bulk promotional messages, updates, and offers to thousands of contacts with one click.'
                            },
                            {
                                'title': 'Meta Messaging Tiers & Daily Limits',
                                'step_type': 'tip',
                                'content': 'Tier 1: 1,000 unique business-initiated contacts / 24h.\nTier 2: 10,000 contacts / 24h.\nTier 3: 100,000 contacts / 24h.\nTier 4: Unlimited.'
                            }
                        ]
                    },
                    {
                        'title': 'Creating & Submitting Templates',
                        'icon': 'FileText',
                        'steps': [
                            {
                                'title': 'Template Components',
                                'step_type': 'text',
                                'content': 'Templates consist of:\n- Header (Text, Image, Video, or Document PDF)\n- Body (Text up to 1024 chars with {{1}}, {{2}} variables)\n- Footer (Short disclaimer text)\n- Buttons (Quick Reply or Call-To-Action URLs)'
                            },
                            {
                                'title': 'Sample High-Converting Template Code',
                                'step_type': 'code',
                                'code_language': 'text',
                                'code_snippet': 'Header: Special Offer inside!\nBody: Hi {{1}}, get {{2}}% off on your next purchase of {{3}}! Use code VIP2026.\nButtons: [ Claim Discount ] [ Visit Store ]',
                                'content': 'Replace {{1}} with Contact Name, {{2}} with Discount %, {{3}} with Product Name.'
                            }
                        ]
                    },
                    {
                        'title': 'Launching a Broadcast Campaign',
                        'icon': 'Send',
                        'steps': [
                            {
                                'title': 'Step-by-Step Campaign Launch Checklist',
                                'step_type': 'checklist',
                                'checklist_items': [
                                    {'text': 'Navigate to Broadcasts ➔ Create Campaign', 'checked': True},
                                    {'text': 'Select Approved Meta Template', 'checked': True},
                                    {'text': 'Choose Target Audience Segment / Tags', 'checked': True},
                                    {'text': 'Map Personalization Variables (Name, Order ID)', 'checked': True},
                                    {'text': 'Set Schedule Time or Launch Immediately', 'checked': True}
                                ]
                            }
                        ]
                    }
                ]
            },

            # ─────────────────────────────────────────────────────────────────
            # 3. WORKFLOWS GUIDE
            # ─────────────────────────────────────────────────────────────────
            {
                'slug': 'workflows',
                'title': 'Visual Flow Builder & Chatbot Workflows Guide',
                'icon': 'GitBranch',
                'category': 'Automation',
                'description': 'Learn how to build complex multi-step automated chatbot flows, conditional branching, AI RAG nodes, and API webhooks.',
                'estimated_time': '18 mins',
                'order': 3,
                'sections': [
                    {
                        'title': 'Workflow Architecture',
                        'icon': 'Info',
                        'steps': [
                            {
                                'title': 'Core Flow Concepts',
                                'step_type': 'text',
                                'content': 'Workflows consist of:\n1. Triggers (Keyword match, new contact, webhook event)\n2. Action Nodes (Send message, AI answer, update CRM, call webhook)\n3. Condition Nodes (If contact tag = VIP, route to agent)\n4. Delays (Wait 5 minutes before follow-up)'
                            },
                            {
                                'title': 'Visual Node Types Reference',
                                'step_type': 'checklist',
                                'checklist_items': [
                                    {'text': 'Send Message Node (Text, Media, Buttons)', 'checked': True},
                                    {'text': 'Ask Question / Collect Input Node', 'checked': True},
                                    {'text': 'AI Knowledge Bot Node (RAG Document Query)', 'checked': True},
                                    {'text': 'Google Sheets Append Node', 'checked': True},
                                    {'text': 'Condition / If-Else Logic Branch Node', 'checked': True},
                                    {'text': 'Transfer to Human Agent Node', 'checked': True}
                                ]
                            }
                        ]
                    },
                    {
                        'title': 'Building an AI Lead Qualification Workflow',
                        'icon': 'Zap',
                        'steps': [
                            {
                                'title': 'Sample Webhook Payload Integration',
                                'step_type': 'code',
                                'code_language': 'json',
                                'code_snippet': '{\n  "event": "lead_captured",\n  "phone": "+919876543210",\n  "name": "Alex Smith",\n  "budget": "5000"\n}',
                                'content': 'Webhooks automatically pass external form data into your workflow variables.'
                            }
                        ]
                    }
                ]
            },

            # ─────────────────────────────────────────────────────────────────
            # 4. SETTINGS GUIDE
            # ─────────────────────────────────────────────────────────────────
            {
                'slug': 'settings',
                'title': 'Workspace Settings & API Keys Guide',
                'icon': 'Settings',
                'category': 'Configuration',
                'description': 'Configure workspace profiles, security settings, team permissions, custom webhooks, and billing subscriptions.',
                'estimated_time': '8 mins',
                'order': 4,
                'sections': [
                    {
                        'title': 'Security & API Tokens',
                        'icon': 'Shield',
                        'steps': [
                            {
                                'title': 'Managing API Keys',
                                'step_type': 'text',
                                'content': 'Your secret UWOConnect API Key authenticates programmatic requests. Never expose this key in public client-side frontend code.'
                            },
                            {
                                'title': 'Generating a Secret Token',
                                'step_type': 'code',
                                'code_language': 'bash',
                                'code_snippet': 'Authorization: Bearer uwoc_live_9f837a2819038472910',
                                'content': 'Include this header in all REST API calls.'
                            }
                        ]
                    }
                ]
            },

            # ─────────────────────────────────────────────────────────────────
            # 5. DASHBOARD & OTHER MODULE GUIDES (Generic Seed)
            # ─────────────────────────────────────────────────────────────────
            {
                'slug': 'dashboard',
                'title': 'Dashboard Overview & Analytics Guide',
                'icon': 'LayoutDashboard',
                'category': 'General',
                'description': 'Understand main metrics, conversation velocity, automation run rates, and quick action launchpads.',
                'estimated_time': '5 mins',
                'order': 5,
                'sections': [
                    {
                        'title': 'Dashboard Metrics',
                        'icon': 'BarChart3',
                        'steps': [
                            {
                                'title': 'Understanding Key Stats',
                                'step_type': 'text',
                                'content': 'Track real-time active conversations, AI bot handling rate, delivery statistics, and agent response times.'
                            }
                        ]
                    }
                ]
            },
            {
                'slug': 'youtube',
                'title': 'YouTube Channel Automation & AI Comments Guide',
                'icon': 'Video',
                'category': 'Social Media',
                'description': 'Connect YouTube channel via OAuth, auto-reply to comments using RAG AI or Custom Keyword rules, and trigger broadcast alerts.',
                'estimated_time': '10 mins',
                'order': 6,
                'sections': [
                    {
                        'title': 'YouTube Integration Setup',
                        'icon': 'Video',
                        'steps': [
                            {
                                'title': 'Connecting Channel',
                                'step_type': 'text',
                                'content': 'Navigate to YouTube tab ➔ Click "Connect Channel" ➔ Grant OAuth permissions for YouTube Data API v3.'
                            },
                            {
                                'title': 'Custom Keyword Auto-Reply Rules',
                                'step_type': 'tip',
                                'content': 'Add rules like "price, cost" ➔ "Check our pricing at https://uwoconnect.com". Keyword rules override AI Gemini generation for instant accuracy.'
                            }
                        ]
                    }
                ]
            },
            {
                'slug': 'crm',
                'title': 'Leads & Contact Management (CRM) Guide',
                'icon': 'Database',
                'category': 'Sales',
                'description': 'Manage contact profiles, lead scoring, tags, custom fields, conversation histories, and bulk CSV imports.',
                'estimated_time': '10 mins',
                'order': 7,
                'sections': [
                    {
                        'title': 'Contact Management',
                        'icon': 'Users',
                        'steps': [
                            {
                                'title': 'Tagging & Lead Scoring',
                                'step_type': 'text',
                                'content': 'Assign tags (VIP, Hot Lead, Qualified) and increment lead scores dynamically inside workflows.'
                            }
                        ]
                    }
                ]
            },
            {
                'slug': 'inbox',
                'title': 'Omnichannel Unified Inbox Guide',
                'icon': 'MessageSquare',
                'category': 'Communication',
                'description': 'Centralized inbox for agents to manage messages across WhatsApp, Instagram, Facebook, Telegram, and Email.',
                'estimated_time': '10 mins',
                'order': 8,
                'sections': [
                    {
                        'title': 'Inbox Features',
                        'icon': 'Inbox',
                        'steps': [
                            {
                                'title': 'Agent Chat Assignment',
                                'step_type': 'text',
                                'content': 'Reassign chats to specialized human agents or transfer back to AI automation at any point.'
                            }
                        ]
                    }
                ]
            },
            {
                'slug': 'knowledge',
                'title': 'AI Knowledge Base (RAG) Guide',
                'icon': 'Brain',
                'category': 'AI & Training',
                'description': 'Upload PDFs, documents, FAQs, and web links to train your custom RAG AI assistant for context-aware customer answers.',
                'estimated_time': '12 mins',
                'order': 9,
                'sections': [
                    {
                        'title': 'Document Training',
                        'icon': 'FileText',
                        'steps': [
                            {
                                'title': 'Uploading PDF & Text Documents',
                                'step_type': 'text',
                                'content': 'Upload business guidelines, refund policies, and product manuals. System automatically creates vector embeddings.'
                            }
                        ]
                    }
                ]
            }
        ]

        # Process seeding
        for g_data in GUIDES_DATA:
            sections_data = g_data.pop('sections', [])
            guide, created = Guide.objects.update_or_create(
                slug=g_data['slug'],
                defaults=g_data
            )
            action = 'Created' if created else 'Updated'
            self.stdout.write(f"  [{action}] Guide: {guide.title}")

            for s_order, s_data in enumerate(sections_data):
                steps_data = s_data.pop('steps', [])
                s_data['guide'] = guide
                s_data['order'] = s_order
                section, _ = GuideSection.objects.update_or_create(
                    guide=guide,
                    title=s_data['title'],
                    defaults=s_data
                )

                for st_order, st_data in enumerate(steps_data):
                    st_data['section'] = section
                    st_data['order'] = st_order
                    GuideStep.objects.update_or_create(
                        section=section,
                        order=st_order,
                        title=st_data.get('title', ''),
                        defaults=st_data
                    )

        self.stdout.write(self.style.SUCCESS('Successfully seeded all Interactive Learning Center guides!'))
