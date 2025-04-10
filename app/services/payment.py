from flask import current_app
from app.models.payment import Payment, PaymentHistory, PaymentDispute
from app import db
from datetime import datetime
import logging
import stripe
from decimal import Decimal

logger = logging.getLogger(__name__)

class PaymentService:
    """Service for handling payment processing, refunds, and disputes"""
    
    @staticmethod
    def process_payment(order_id, amount, currency, payment_method_id, customer_id):
        """
        Process a payment for an order
        
        Args:
            order_id (int): ID of the order
            amount (Decimal): Payment amount
            currency (str): Currency code (e.g., 'USD')
            payment_method_id (str): Stripe payment method ID
            customer_id (str): Stripe customer ID
            
        Returns:
            dict: Payment result including status and payment details
        """
        try:
            # Create payment intent with Stripe
            intent = stripe.PaymentIntent.create(
                amount=int(amount * 100),  # Convert to cents
                currency=currency.lower(),
                payment_method=payment_method_id,
                customer=customer_id,
                confirm=True,
                return_url=current_app.config['PAYMENT_RETURN_URL']
            )
            
            # Create payment record
            payment = Payment(
                order_id=order_id,
                amount=amount,
                currency=currency,
                payment_method=payment_method_id,
                payment_intent_id=intent.id,
                status=intent.status,
                metadata={
                    'customer_id': customer_id,
                    'payment_method_type': intent.payment_method_types[0]
                }
            )
            
            db.session.add(payment)
            
            # Record payment history
            PaymentService._record_payment_history(
                payment.id,
                intent.status,
                'payment',
                {'payment_intent_id': intent.id}
            )
            
            db.session.commit()
            
            return {
                'success': True,
                'payment': payment.to_dict(),
                'client_secret': intent.client_secret
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error processing payment: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error processing payment: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': 'An unexpected error occurred'
            }
    
    @staticmethod
    def process_refund(payment_id, amount=None, reason=None):
        """
        Process a refund for a payment
        
        Args:
            payment_id (int): ID of the payment to refund
            amount (Decimal, optional): Amount to refund. If None, refunds the full amount.
            reason (str, optional): Reason for the refund
            
        Returns:
            dict: Refund result including status and refund details
        """
        try:
            payment = Payment.query.get(payment_id)
            if not payment:
                return {
                    'success': False,
                    'message': "Payment not found"
                }
            
            # Check if payment is eligible for refund
            if payment.status not in ['succeeded', 'paid']:
                return {
                    'success': False,
                    'message': f"Payment with status '{payment.status}' cannot be refunded"
                }
            
            # Check if already fully refunded
            if payment.refunded_amount and payment.refunded_amount >= payment.amount:
                return {
                    'success': False,
                    'message': "Payment has already been fully refunded"
                }
            
            # Determine refund amount
            refund_amount = amount
            if refund_amount is None:
                # Full refund
                refund_amount = payment.amount - (payment.refunded_amount or 0)
            else:
                # Partial refund
                refund_amount = Decimal(str(refund_amount))
                remaining_amount = payment.amount - (payment.refunded_amount or 0)
                if refund_amount > remaining_amount:
                    return {
                        'success': False,
                        'message': f"Refund amount exceeds remaining amount ({remaining_amount})"
                    }
            
            # Process refund with Stripe
            try:
                refund = stripe.Refund.create(
                    payment_intent=payment.payment_intent_id,
                    amount=int(refund_amount * 100),  # Convert to cents
                    reason=reason
                )
                
                # Update payment record
                payment.refunded_amount = (payment.refunded_amount or 0) + refund_amount
                payment.refunded_at = datetime.utcnow()
                
                # Update payment status
                if payment.refunded_amount >= payment.amount:
                    payment.status = 'refunded'
                else:
                    payment.status = 'partially_refunded'
                
                # Record refund in payment history
                PaymentService._record_payment_history(
                    payment_id=payment_id,
                    status='succeeded',
                    type='refund',
                    details={
                        'refund_id': refund.id,
                        'amount': float(refund_amount),
                        'reason': reason,
                        'stripe_refund_id': refund.id
                    }
                )
                
                db.session.commit()
                
                return {
                    'success': True,
                    'message': "Refund processed successfully",
                    'data': {
                        'payment_id': payment_id,
                        'refund_id': refund.id,
                        'amount': float(refund_amount),
                        'status': payment.status,
                        'refunded_amount': float(payment.refunded_amount),
                        'remaining_amount': float(payment.amount - payment.refunded_amount)
                    }
                }
                
            except stripe.error.StripeError as e:
                # Record failed refund attempt
                PaymentService._record_payment_history(
                    payment_id=payment_id,
                    status='failed',
                    type='refund',
                    details={
                        'amount': float(refund_amount),
                        'reason': reason,
                        'error': str(e)
                    }
                )
                
                db.session.commit()
                
                return {
                    'success': False,
                    'message': f"Stripe refund failed: {str(e)}"
                }
                
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error processing refund: {str(e)}")
            return {
                'success': False,
                'message': f"Error processing refund: {str(e)}"
            }
    
    @staticmethod
    def create_payment_dispute(payment_id, reason, evidence):
        """
        Create a payment dispute
        
        Args:
            payment_id (int): ID of the payment
            reason (str): Reason for the dispute
            evidence (dict): Evidence supporting the dispute
            
        Returns:
            dict: Dispute result including status and dispute details
        """
        try:
            payment = Payment.query.get(payment_id)
            if not payment:
                return {
                    'success': False,
                    'error': 'Payment not found'
                }
            
            # Create dispute with Stripe
            dispute = stripe.Dispute.create(
                payment_intent=payment.payment_intent_id,
                evidence=evidence,
                reason=reason
            )
            
            # Create dispute record
            payment_dispute = PaymentDispute(
                payment_id=payment_id,
                dispute_id=dispute.id,
                reason=reason,
                evidence=evidence,
                status=dispute.status,
                amount=payment.amount
            )
            
            db.session.add(payment_dispute)
            
            # Update payment status
            payment.status = 'disputed'
            
            # Record dispute history
            PaymentService._record_payment_history(
                payment.id,
                'disputed',
                'dispute',
                {
                    'dispute_id': dispute.id,
                    'reason': reason
                }
            )
            
            db.session.commit()
            
            return {
                'success': True,
                'dispute': payment_dispute.to_dict()
            }
            
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error creating dispute: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': str(e)
            }
        except Exception as e:
            logger.error(f"Error creating dispute: {str(e)}")
            db.session.rollback()
            return {
                'success': False,
                'error': 'An unexpected error occurred'
            }
    
    @staticmethod
    def get_payment_history(payment_id):
        """
        Get payment history for a payment
        
        Args:
            payment_id (int): ID of the payment
            
        Returns:
            list: List of payment history records
        """
        history = PaymentHistory.query.filter_by(payment_id=payment_id).order_by(PaymentHistory.created_at.desc()).all()
        return [record.to_dict() for record in history]
    
    @staticmethod
    def _record_payment_history(payment_id, status, type, details=None):
        """
        Record a payment history entry
        
        Args:
            payment_id (int): ID of the payment
            status (str): Status of the payment event
            type (str): Type of payment event
            details (dict, optional): Additional details about the event
        """
        history = PaymentHistory(
            payment_id=payment_id,
            status=status,
            type=type,
            details=details
        )
        db.session.add(history)
    
    @staticmethod
    def get_payment_methods(customer_id):
        """
        Get payment methods for a customer
        
        Args:
            customer_id (str): Stripe customer ID
            
        Returns:
            list: List of payment methods
        """
        try:
            payment_methods = stripe.PaymentMethod.list(
                customer=customer_id,
                type='card'
            )
            return payment_methods.data
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error getting payment methods: {str(e)}")
            return []
    
    @staticmethod
    def attach_payment_method(customer_id, payment_method_id):
        """
        Attach a payment method to a customer
        
        Args:
            customer_id (str): Stripe customer ID
            payment_method_id (str): Stripe payment method ID
            
        Returns:
            dict: Result of attaching the payment method
        """
        try:
            payment_method = stripe.PaymentMethod.attach(
                payment_method_id,
                customer=customer_id
            )
            return {
                'success': True,
                'payment_method': payment_method
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error attaching payment method: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def detach_payment_method(payment_method_id):
        """
        Detach a payment method from a customer
        
        Args:
            payment_method_id (str): Stripe payment method ID
            
        Returns:
            dict: Result of detaching the payment method
        """
        try:
            payment_method = stripe.PaymentMethod.detach(payment_method_id)
            return {
                'success': True,
                'payment_method': payment_method
            }
        except stripe.error.StripeError as e:
            logger.error(f"Stripe error detaching payment method: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            } 