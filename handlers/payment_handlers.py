"""
Payment Flow Handlers Module

This module contains handlers for managing payment flows including offer buttons,
transaction processing, and payment status updates.
"""

from typing import Optional, Dict, Any, Callable
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class PaymentStatus(Enum):
    """Enumeration of possible payment statuses."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class OfferType(Enum):
    """Enumeration of offer types."""
    DISCOUNT = "discount"
    BUNDLE = "bundle"
    LIMITED_TIME = "limited_time"
    LOYALTY = "loyalty"
    REFERRAL = "referral"


@dataclass
class Offer:
    """Data class representing a payment offer."""
    offer_id: str
    offer_type: OfferType
    description: str
    discount_percent: Optional[float] = None
    discount_amount: Optional[float] = None
    expiration_date: Optional[datetime] = None
    conditions: Optional[Dict[str, Any]] = None
    
    def is_expired(self) -> bool:
        """Check if the offer has expired."""
        if self.expiration_date is None:
            return False
        return datetime.utcnow() > self.expiration_date
    
    def apply_to_amount(self, amount: float) -> float:
        """Calculate the final amount after applying the offer."""
        if self.is_expired():
            return amount
        
        if self.discount_percent:
            return amount * (1 - self.discount_percent / 100)
        elif self.discount_amount:
            return max(0, amount - self.discount_amount)
        
        return amount


@dataclass
class PaymentTransaction:
    """Data class representing a payment transaction."""
    transaction_id: str
    amount: float
    currency: str = "USD"
    status: PaymentStatus = PaymentStatus.PENDING
    offer: Optional[Offer] = None
    created_at: datetime = None
    updated_at: datetime = None
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        """Initialize datetime fields if not provided."""
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.updated_at is None:
            self.updated_at = datetime.utcnow()
    
    def get_final_amount(self) -> float:
        """Get the final amount after applying any offers."""
        if self.offer:
            return self.offer.apply_to_amount(self.amount)
        return self.amount


class OfferButtonHandler:
    """Handler for offer button interactions."""
    
    def __init__(self):
        """Initialize the offer button handler."""
        self.active_offers: Dict[str, Offer] = {}
        self.callbacks: Dict[str, list[Callable]] = {
            'on_offer_clicked': [],
            'on_offer_applied': [],
            'on_offer_expired': [],
        }
    
    def register_offer(self, offer: Offer) -> None:
        """
        Register a new offer.
        
        Args:
            offer: The offer to register
        """
        self.active_offers[offer.offer_id] = offer
    
    def remove_offer(self, offer_id: str) -> bool:
        """
        Remove an offer by ID.
        
        Args:
            offer_id: The ID of the offer to remove
            
        Returns:
            True if offer was removed, False if not found
        """
        if offer_id in self.active_offers:
            del self.active_offers[offer_id]
            return True
        return False
    
    def get_offer(self, offer_id: str) -> Optional[Offer]:
        """
        Retrieve an offer by ID.
        
        Args:
            offer_id: The ID of the offer
            
        Returns:
            The offer if found and not expired, None otherwise
        """
        offer = self.active_offers.get(offer_id)
        if offer and not offer.is_expired():
            return offer
        return None
    
    def handle_offer_button_click(self, offer_id: str, transaction_id: str) -> bool:
        """
        Handle offer button click event.
        
        Args:
            offer_id: The ID of the clicked offer
            transaction_id: The ID of the associated transaction
            
        Returns:
            True if offer was successfully applied, False otherwise
        """
        offer = self.get_offer(offer_id)
        if not offer:
            return False
        
        # Trigger callbacks
        self._trigger_callbacks('on_offer_clicked', offer_id, transaction_id)
        return True
    
    def apply_offer_to_transaction(self, transaction: PaymentTransaction, offer_id: str) -> bool:
        """
        Apply an offer to a transaction.
        
        Args:
            transaction: The transaction to apply the offer to
            offer_id: The ID of the offer to apply
            
        Returns:
            True if offer was successfully applied, False otherwise
        """
        offer = self.get_offer(offer_id)
        if not offer:
            return False
        
        transaction.offer = offer
        transaction.updated_at = datetime.utcnow()
        
        # Trigger callbacks
        self._trigger_callbacks('on_offer_applied', transaction.transaction_id, offer_id)
        return True
    
    def get_available_offers(self) -> list[Offer]:
        """
        Get all currently available (non-expired) offers.
        
        Returns:
            List of available offers
        """
        return [
            offer for offer in self.active_offers.values()
            if not offer.is_expired()
        ]
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """
        Register a callback for an event.
        
        Args:
            event: The event name
            callback: The callback function
        """
        if event in self.callbacks:
            self.callbacks[event].append(callback)
    
    def _trigger_callbacks(self, event: str, *args, **kwargs) -> None:
        """
        Trigger all registered callbacks for an event.
        
        Args:
            event: The event name
            *args: Positional arguments to pass to callbacks
            **kwargs: Keyword arguments to pass to callbacks
        """
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"Error in callback for event '{event}': {e}")


class PaymentFlowHandler:
    """Main handler for payment flows."""
    
    def __init__(self):
        """Initialize the payment flow handler."""
        self.transactions: Dict[str, PaymentTransaction] = {}
        self.offer_handler = OfferButtonHandler()
    
    def create_transaction(
        self,
        transaction_id: str,
        amount: float,
        currency: str = "USD",
        metadata: Optional[Dict[str, Any]] = None
    ) -> PaymentTransaction:
        """
        Create a new payment transaction.
        
        Args:
            transaction_id: Unique transaction ID
            amount: Transaction amount
            currency: Currency code (default: USD)
            metadata: Additional transaction metadata
            
        Returns:
            The created transaction
        """
        transaction = PaymentTransaction(
            transaction_id=transaction_id,
            amount=amount,
            currency=currency,
            metadata=metadata or {}
        )
        self.transactions[transaction_id] = transaction
        return transaction
    
    def get_transaction(self, transaction_id: str) -> Optional[PaymentTransaction]:
        """
        Retrieve a transaction by ID.
        
        Args:
            transaction_id: The transaction ID
            
        Returns:
            The transaction if found, None otherwise
        """
        return self.transactions.get(transaction_id)
    
    def update_transaction_status(
        self,
        transaction_id: str,
        status: PaymentStatus
    ) -> bool:
        """
        Update the status of a transaction.
        
        Args:
            transaction_id: The transaction ID
            status: The new status
            
        Returns:
            True if updated successfully, False if transaction not found
        """
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            return False
        
        transaction.status = status
        transaction.updated_at = datetime.utcnow()
        return True
    
    def process_payment(self, transaction_id: str) -> bool:
        """
        Process a payment transaction.
        
        Args:
            transaction_id: The transaction ID
            
        Returns:
            True if processing started successfully, False otherwise
        """
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            return False
        
        if transaction.status != PaymentStatus.PENDING:
            return False
        
        # Update status to processing
        self.update_transaction_status(transaction_id, PaymentStatus.PROCESSING)
        
        # Here you would integrate with payment gateway
        # For now, we'll simulate successful processing
        self.update_transaction_status(transaction_id, PaymentStatus.COMPLETED)
        
        return True
    
    def refund_transaction(self, transaction_id: str) -> bool:
        """
        Refund a transaction.
        
        Args:
            transaction_id: The transaction ID
            
        Returns:
            True if refund was processed, False otherwise
        """
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            return False
        
        if transaction.status not in [PaymentStatus.COMPLETED, PaymentStatus.PROCESSING]:
            return False
        
        self.update_transaction_status(transaction_id, PaymentStatus.REFUNDED)
        return True
    
    def get_payment_summary(self, transaction_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a summary of a payment transaction.
        
        Args:
            transaction_id: The transaction ID
            
        Returns:
            Payment summary dict or None if transaction not found
        """
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            return None
        
        final_amount = transaction.get_final_amount()
        savings = transaction.amount - final_amount if transaction.offer else 0
        
        return {
            'transaction_id': transaction.transaction_id,
            'original_amount': transaction.amount,
            'offer_applied': transaction.offer is not None,
            'final_amount': final_amount,
            'savings': savings,
            'currency': transaction.currency,
            'status': transaction.status.value,
            'created_at': transaction.created_at.isoformat(),
            'updated_at': transaction.updated_at.isoformat(),
        }


# Convenience function to create a default payment flow handler
def create_payment_handler() -> PaymentFlowHandler:
    """
    Factory function to create a payment flow handler.
    
    Returns:
        A new PaymentFlowHandler instance
    """
    return PaymentFlowHandler()
