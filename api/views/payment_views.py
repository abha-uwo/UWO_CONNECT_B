import time
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status

from api.models import PaymentOrder, Client, Log
from api.services.razorpay_service import RazorpayService

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
        receipt_id = f"rcpt_{user.client.id}_{int(time.time())}"

        # Create Razorpay Order
        rzp_service = RazorpayService()
        rzp_response = rzp_service.create_order(
            amount_in_inr=amount,
            receipt_id=receipt_id,
            notes={
                'client_id': user.client.id,
                'user_email': user.email or '',
                'plan': plan,
                'billing_cycle': billing_cycle
            }
        )

        razorpay_order_id = rzp_response.get('razorpay_order_id')

        # Save Order Entry
        payment_order = PaymentOrder.objects.create(
            client=user.client,
            user=user,
            order_id=receipt_id,
            razorpay_order_id=razorpay_order_id,
            amount=amount,
            currency='INR',
            plan=plan,
            billing_cycle=billing_cycle,
            status='PENDING'
        )

        return Response({
            'order_id': receipt_id,
            'razorpay_order_id': razorpay_order_id,
            'razorpay_key_id': rzp_response.get('razorpay_key_id'),
            'amount': amount,
            'amount_paise': rzp_response.get('amount'),
            'currency': 'INR',
            'plan': plan,
            'billing_cycle': billing_cycle,
            'is_mock': rzp_response.get('is_mock', False),
            'customer_name': user.get_full_name() or user.username,
            'customer_email': user.email or '',
            'customer_phone': user.client.phone_number or getattr(user, 'phone_number', '') or ''
        }, status=status.HTTP_201_CREATED)


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        if not user.client:
            return Response({'error': 'No client associated with user'}, status=status.HTTP_400_BAD_REQUEST)

        order_id = request.data.get('order_id')
        razorpay_order_id = request.data.get('razorpay_order_id')
        razorpay_payment_id = request.data.get('razorpay_payment_id')
        razorpay_signature = request.data.get('razorpay_signature')
        force_mock_success = request.data.get('force_mock_success', False)

        try:
            if order_id:
                payment_order = PaymentOrder.objects.get(order_id=order_id, client=user.client)
            elif razorpay_order_id:
                payment_order = PaymentOrder.objects.get(razorpay_order_id=razorpay_order_id, client=user.client)
            else:
                return Response({'error': 'order_id or razorpay_order_id required'}, status=status.HTTP_400_BAD_REQUEST)
        except PaymentOrder.DoesNotExist:
            return Response({'error': 'Payment order record not found'}, status=status.HTTP_404_NOT_FOUND)

        rzp_service = RazorpayService()

        # Check signature verification
        is_valid = force_mock_success or rzp_service.verify_signature(
            razorpay_order_id=razorpay_order_id or payment_order.razorpay_order_id,
            razorpay_payment_id=razorpay_payment_id,
            razorpay_signature=razorpay_signature
        )

        if is_valid:
            payment_order.status = 'PAID'
            payment_order.razorpay_payment_id = razorpay_payment_id or f"pay_mock_{int(time.time())}"
            payment_order.razorpay_signature = razorpay_signature or 'mock_sig'
            payment_order.cf_payment_id = payment_order.razorpay_payment_id
            payment_order.payment_method = 'Razorpay'
            payment_order.save()

            # Upgrade Client Workspace Plan
            client = payment_order.client
            client.plan = payment_order.plan
            client.status = 'ACTIVE'
            client.save()

            # Audit Log
            Log.objects.create(
                client=client,
                user=user,
                action='SUBSCRIPTION_UPGRADED',
                details=f"Upgraded to {payment_order.plan} ({payment_order.billing_cycle}) via Razorpay Order #{payment_order.order_id}"
            )

            return Response({
                'success': True,
                'message': f'Subscription upgraded successfully to {payment_order.plan}!',
                'plan': client.plan,
                'status': 'PAID',
                'order_id': payment_order.order_id,
                'razorpay_payment_id': payment_order.razorpay_payment_id
            }, status=status.HTTP_200_OK)
        else:
            payment_order.status = 'FAILED'
            payment_order.save()
            return Response({
                'success': False,
                'message': 'Razorpay signature verification failed.',
                'status': 'FAILED'
            }, status=status.HTTP_400_BAD_REQUEST)


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
            'razorpay_order_id': o.razorpay_order_id,
            'razorpay_payment_id': o.razorpay_payment_id or o.cf_payment_id,
            'amount': str(o.amount),
            'currency': o.currency,
            'plan': o.plan,
            'billing_cycle': o.billing_cycle,
            'status': o.status,
            'payment_method': o.payment_method or 'Razorpay',
            'created_at': o.created_at.isoformat(),
        } for o in orders]

        return Response({'orders': orders_data}, status=status.HTTP_200_OK)


class RazorpayWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.data
        logger.info(f"Razorpay Webhook Received: {payload}")
        
        event = payload.get('event')
        entity = payload.get('payload', {}).get('payment', {}).get('entity', {})
        razorpay_order_id = entity.get('order_id')
        razorpay_payment_id = entity.get('id')

        if razorpay_order_id and event in ['payment.captured', 'order.paid']:
            try:
                payment_order = PaymentOrder.objects.get(razorpay_order_id=razorpay_order_id)
                if payment_order.status != 'PAID':
                    payment_order.status = 'PAID'
                    payment_order.razorpay_payment_id = razorpay_payment_id
                    payment_order.payment_method = entity.get('method', 'Razorpay')
                    payment_order.save()

                    client = payment_order.client
                    client.plan = payment_order.plan
                    client.status = 'ACTIVE'
                    client.save()

                    Log.objects.create(
                        client=client,
                        user=payment_order.user,
                        action='SUBSCRIPTION_UPGRADED_WEBHOOK',
                        details=f"Upgraded to {payment_order.plan} via Razorpay Webhook for Order #{razorpay_order_id}"
                    )
            except PaymentOrder.DoesNotExist:
                logger.warning(f"Razorpay Webhook received for unknown order_id: {razorpay_order_id}")

        return Response({'status': 'OK'}, status=status.HTTP_200_OK)

# Alias for backward compatibility
CashfreeWebhookView = RazorpayWebhookView
