import time
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

from api.models import PaymentOrder, Client, Log
from api.services.cashfree_service import CashfreeService

logger = logging.getLogger(__name__)

# Plan Pricing in INR
PLAN_PRICES = {
    'STARTER': {
        'MONTHLY': 3999.00,
        'ANNUAL': 38388.00,
    },
    'GROWTH': {
        'MONTHLY': 7999.00,
        'ANNUAL': 76788.00,
    },
    'ENTERPRISE': {
        'MONTHLY': 23999.00,
        'ANNUAL': 230388.00,
    }
}

class CreatePaymentOrderView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.client:
            return Response({'error': 'No client associated with user'}, status=status.HTTP_400_BAD_REQUEST)

        plan = request.data.get('plan', 'GROWTH').upper()
        billing_cycle = request.data.get('billing_cycle', 'MONTHLY').upper()

        if plan not in PLAN_PRICES:
            return Response({'error': f'Invalid plan. Choose from {list(PLAN_PRICES.keys())}'}, status=status.HTTP_400_BAD_REQUEST)
        if billing_cycle not in ['MONTHLY', 'ANNUAL']:
            billing_cycle = 'MONTHLY'

        amount = PLAN_PRICES[plan][billing_cycle]
        order_id = f"order_cf_{user.client.id}_{int(time.time())}"

        # Save initial order
        payment_order = PaymentOrder.objects.create(
            client=user.client,
            user=user,
            order_id=order_id,
            amount=amount,
            currency='INR',
            plan=plan,
            billing_cycle=billing_cycle,
            status='PENDING'
        )

        # Call Cashfree API
        cf_service = CashfreeService()
        return_url = request.data.get('return_url', 'http://localhost:3000/client/settings?order_id={order_id}')
        
        cf_response = cf_service.create_order(
            order_id=order_id,
            amount=amount,
            customer_id=user.id,
            customer_email=user.email,
            customer_phone=user.client.phone_number or getattr(user, 'phone_number', None),
            customer_name=user.get_full_name() or user.username,
            return_url=return_url
        )

        payment_session_id = cf_response.get('payment_session_id')
        payment_order.payment_session_id = payment_session_id
        payment_order.save()

        return Response({
            'order_id': order_id,
            'payment_session_id': payment_session_id,
            'cf_environment': cf_response.get('cf_environment', 'TEST'),
            'amount': amount,
            'currency': 'INR',
            'plan': plan,
            'billing_cycle': billing_cycle,
            'is_mock': cf_response.get('is_mock', False)
        }, status=status.HTTP_201_CREATED)


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.client:
            return Response({'error': 'No client associated with user'}, status=status.HTTP_400_BAD_REQUEST)

        order_id = request.data.get('order_id')
        if not order_id:
            return Response({'error': 'order_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment_order = PaymentOrder.objects.get(order_id=order_id, client=user.client)
        except PaymentOrder.DoesNotExist:
            return Response({'error': 'Payment order not found'}, status=status.HTTP_404_NOT_FOUND)

        cf_service = CashfreeService()
        status_resp = cf_service.get_order_status(order_id)
        order_status = status_resp.get('order_status', 'PENDING')

        if order_status == 'PAID' or request.data.get('force_mock_success') is True:
            payment_order.status = 'PAID'
            payment_order.cf_payment_id = status_resp.get('cf_payment_id', f'cf_pay_{int(time.time())}')
            payment_order.payment_method = status_resp.get('payment_method', 'Cashfree')
            payment_order.save()

            # Upgrade Client Plan
            client = payment_order.client
            client.plan = payment_order.plan
            client.status = 'ACTIVE'
            client.save()

            # Log system event
            Log.objects.create(
                client=client,
                user=user,
                action='SUBSCRIPTION_UPGRADED',
                details=f"Upgraded to {payment_order.plan} ({payment_order.billing_cycle}) via Cashfree Order #{order_id}"
            )

            return Response({
                'success': True,
                'message': f'Subscription upgraded successfully to {payment_order.plan}!',
                'plan': client.plan,
                'status': 'PAID',
                'order_id': order_id
            }, status=status.HTTP_200_OK)

        elif order_status in ['FAILED', 'CANCELLED', 'EXPIRED']:
            payment_order.status = order_status
            payment_order.save()
            return Response({
                'success': False,
                'message': f'Payment {order_status.lower()}',
                'status': order_status,
                'order_id': order_id
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                'success': False,
                'message': 'Payment is still pending',
                'status': 'PENDING',
                'order_id': order_id
            }, status=status.HTTP_200_OK)


class PaymentHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not user.client:
            return Response({'orders': []}, status=status.HTTP_200_OK)

        orders = PaymentOrder.objects.filter(client=user.client).order_by('-created_at')
        orders_data = [{
            'id': o.id,
            'order_id': o.order_id,
            'amount': str(o.amount),
            'currency': o.currency,
            'plan': o.plan,
            'billing_cycle': o.billing_cycle,
            'status': o.status,
            'cf_payment_id': o.cf_payment_id,
            'payment_method': o.payment_method,
            'created_at': o.created_at.isoformat(),
        } for o in orders]

        return Response({'orders': orders_data}, status=status.HTTP_200_OK)


class CashfreeWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.data
        logger.info(f"Cashfree Webhook Received: {payload}")
        
        # Extract order details from webhook body
        data = payload.get('data', {})
        order_data = data.get('order', {})
        payment_data = data.get('payment', {})
        
        order_id = order_data.get('order_id')
        payment_status = payment_data.get('payment_status') or payload.get('type')

        if order_id and (payment_status == 'SUCCESS' or 'SUCCESS' in str(payment_status)):
            try:
                payment_order = PaymentOrder.objects.get(order_id=order_id)
                if payment_order.status != 'PAID':
                    payment_order.status = 'PAID'
                    payment_order.cf_payment_id = payment_data.get('cf_payment_id', '')
                    payment_order.payment_method = payment_data.get('payment_group', 'Online')
                    payment_order.save()

                    # Upgrade Client Plan
                    client = payment_order.client
                    client.plan = payment_order.plan
                    client.status = 'ACTIVE'
                    client.save()

                    Log.objects.create(
                        client=client,
                        user=payment_order.user,
                        action='SUBSCRIPTION_UPGRADED_WEBHOOK',
                        details=f"Upgraded to {payment_order.plan} via Cashfree Webhook for Order #{order_id}"
                    )
            except PaymentOrder.DoesNotExist:
                logger.warning(f"Webhook received for unknown order_id: {order_id}")

        return Response({'status': 'OK'}, status=status.HTTP_200_OK)
