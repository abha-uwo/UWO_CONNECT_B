import os
import requests
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class CashfreeService:
    def __init__(self):
        self.app_id = getattr(settings, 'CASHFREE_APP_ID', os.getenv('CASHFREE_APP_ID', ''))
        self.secret_key = getattr(settings, 'CASHFREE_SECRET_KEY', os.getenv('CASHFREE_SECRET_KEY', ''))
        self.env = getattr(settings, 'CASHFREE_ENV', os.getenv('CASHFREE_ENV', 'TEST')).upper()
        self.api_version = '2023-08-01'
        
        if self.env == 'PRODUCTION':
            self.base_url = 'https://api.cashfree.com/pg'
        else:
            self.base_url = 'https://sandbox.cashfree.com/pg'

    def get_headers(self):
        return {
            'x-client-id': self.app_id,
            'x-client-secret': self.secret_key,
            'x-api-version': self.api_version,
            'Content-Type': 'application/json',
        }

    def create_order(self, order_id, amount, customer_id, customer_email=None, customer_phone=None, customer_name=None, return_url=None):
        """
        Creates an order with Cashfree PG API v3.
        Returns dict containing payment_session_id, order_id, and status.
        """
        if not return_url:
            return_url = "http://localhost:3000/client/settings?order_id={order_id}"

        # Ensure valid phone format (10 digits minimum)
        clean_phone = ''.join(filter(str.isdigit, str(customer_phone or '')))
        if len(clean_phone) < 10:
            clean_phone = '9999999999'

        payload = {
            'order_id': order_id,
            'order_amount': float(amount),
            'order_currency': 'INR',
            'customer_details': {
                'customer_id': str(customer_id),
                'customer_name': customer_name or 'Valued Customer',
                'customer_email': customer_email or 'customer@connectwa.com',
                'customer_phone': clean_phone[-10:],
            },
            'order_meta': {
                'return_url': return_url
            }
        }

        # If credentials are not set up, provide a graceful test fallback for local dev
        if not self.app_id or not self.secret_key:
            logger.warning("CASHFREE_APP_ID or CASHFREE_SECRET_KEY not set. Using test sandbox mock mode.")
            return {
                'order_id': order_id,
                'payment_session_id': f'session_mock_sandbox_{order_id}',
                'cf_environment': 'TEST',
                'is_mock': True,
            }

        try:
            url = f"{self.base_url}/orders"
            res = requests.post(url, json=payload, headers=self.get_headers(), timeout=10)
            data = res.json()

            if res.status_code in [200, 201] and 'payment_session_id' in data:
                return {
                    'order_id': data.get('order_id', order_id),
                    'payment_session_id': data.get('payment_session_id'),
                    'cf_environment': self.env,
                    'is_mock': False,
                }
            else:
                logger.error(f"Cashfree API Error: {res.status_code} - {data}")
                # Fallback to test session mode if sandbox credentials fail
                return {
                    'order_id': order_id,
                    'payment_session_id': f'session_mock_sandbox_{order_id}',
                    'cf_environment': 'TEST',
                    'is_mock': True,
                    'error_message': data.get('message', 'Failed to create Cashfree session')
                }
        except Exception as e:
            logger.error(f"Cashfree Connection Exception: {str(e)}")
            return {
                'order_id': order_id,
                'payment_session_id': f'session_mock_sandbox_{order_id}',
                'cf_environment': 'TEST',
                'is_mock': True,
                'error_message': str(e)
            }

    def get_order_status(self, order_id):
        """
        Fetches order status from Cashfree.
        """
        if not self.app_id or not self.secret_key or order_id.startswith('order_mock_') or 'mock' in order_id:
            # Mock mode auto-succeeds
            return {
                'order_id': order_id,
                'order_status': 'PAID',
                'cf_payment_id': f'cf_pay_mock_{order_id}',
                'payment_method': 'UPI',
                'is_mock': True
            }

        try:
            url = f"{self.base_url}/orders/{order_id}"
            res = requests.get(url, headers=self.get_headers(), timeout=10)
            data = res.json()
            if res.status_code == 200:
                order_status = data.get('order_status', 'PENDING')
                return {
                    'order_id': data.get('order_id'),
                    'order_status': order_status,
                    'cf_payment_id': data.get('cf_order_id'),
                    'payment_method': 'Cashfree Online',
                    'is_mock': False,
                    'raw_data': data
                }
            else:
                return {
                    'order_id': order_id,
                    'order_status': 'PENDING',
                    'error_message': data.get('message', 'Could not fetch status')
                }
        except Exception as e:
            logger.error(f"Cashfree Get Order Exception: {str(e)}")
            return {
                'order_id': order_id,
                'order_status': 'PENDING',
                'error_message': str(e)
            }
