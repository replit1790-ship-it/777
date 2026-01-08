"""
Payment Offer and Terms Handler

This module handles payment offers, terms negotiation, and offer management.
It provides functionality for creating, validating, and managing payment offers
with various terms, discounts, and conditions.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, List, Dict, Any
from decimal import Decimal
import json


class OfferType(Enum):
    """Types of payment offers."""
    STANDARD = "standard"
    PROMOTIONAL = "promotional"
    LOYALTY = "loyalty"
    BULK_DISCOUNT = "bulk_discount"
    SEASONAL = "seasonal"
    CUSTOM = "custom"


class OfferStatus(Enum):
    """Status of a payment offer."""
    DRAFT = "draft"
    ACTIVE = "active"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    ACCEPTED = "accepted"


class TermsType(Enum):
    """Types of payment terms."""
    IMMEDIATE = "immediate"
    NET_30 = "net_30"
    NET_60 = "net_60"
    NET_90 = "net_90"
    CUSTOM = "custom"


@dataclass
class PaymentTerms:
    """Represents payment terms for an offer."""
    
    terms_type: TermsType
    days_until_due: int
    early_payment_discount: Optional[Decimal] = None
    late_payment_penalty: Optional[Decimal] = None
    min_payment: Optional[Decimal] = None
    installments: Optional[int] = None
    installment_frequency: Optional[str] = None  # e.g., "weekly", "monthly"
    
    def __post_init__(self):
        """Validate terms configuration."""
        if self.early_payment_discount and not (Decimal(0) <= self.early_payment_discount <= Decimal(100)):
            raise ValueError("Early payment discount must be between 0-100%")
        
        if self.late_payment_penalty and not (Decimal(0) <= self.late_payment_penalty <= Decimal(100)):
            raise ValueError("Late payment penalty must be between 0-100%")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert terms to dictionary."""
        return {
            "terms_type": self.terms_type.value,
            "days_until_due": self.days_until_due,
            "early_payment_discount": float(self.early_payment_discount) if self.early_payment_discount else None,
            "late_payment_penalty": float(self.late_payment_penalty) if self.late_payment_penalty else None,
            "min_payment": float(self.min_payment) if self.min_payment else None,
            "installments": self.installments,
            "installment_frequency": self.installment_frequency,
        }


@dataclass
class PaymentOffer:
    """Represents a payment offer with terms and conditions."""
    
    offer_id: str
    customer_id: str
    amount: Decimal
    currency: str = "USD"
    offer_type: OfferType = OfferType.STANDARD
    status: OfferStatus = OfferStatus.DRAFT
    
    # Offer details
    description: Optional[str] = None
    terms: Optional[PaymentTerms] = None
    discount_percentage: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    
    # Validity
    created_at: datetime = field(default_factory=datetime.utcnow)
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    
    # Additional metadata
    notes: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate offer configuration."""
        if self.discount_percentage and not (Decimal(0) <= self.discount_percentage <= Decimal(100)):
            raise ValueError("Discount percentage must be between 0-100%")
        
        if self.discount_amount and self.discount_amount < 0:
            raise ValueError("Discount amount cannot be negative")
        
        if self.valid_from and self.valid_until and self.valid_from > self.valid_until:
            raise ValueError("valid_from must be before valid_until")
    
    def is_expired(self) -> bool:
        """Check if offer has expired."""
        if not self.valid_until:
            return False
        return datetime.utcnow() > self.valid_until
    
    def is_active(self) -> bool:
        """Check if offer is currently active."""
        now = datetime.utcnow()
        
        if self.status != OfferStatus.ACTIVE:
            return False
        
        if self.valid_from and now < self.valid_from:
            return False
        
        if self.valid_until and now > self.valid_until:
            return False
        
        return True
    
    def calculate_total_amount(self) -> Decimal:
        """Calculate total amount after discounts."""
        total = self.amount
        
        if self.discount_percentage:
            discount = total * (self.discount_percentage / Decimal(100))
            total -= discount
        
        if self.discount_amount:
            total -= self.discount_amount
        
        return max(total, Decimal(0))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert offer to dictionary."""
        return {
            "offer_id": self.offer_id,
            "customer_id": self.customer_id,
            "amount": float(self.amount),
            "currency": self.currency,
            "offer_type": self.offer_type.value,
            "status": self.status.value,
            "description": self.description,
            "terms": self.terms.to_dict() if self.terms else None,
            "discount_percentage": float(self.discount_percentage) if self.discount_percentage else None,
            "discount_amount": float(self.discount_amount) if self.discount_amount else None,
            "created_at": self.created_at.isoformat(),
            "valid_from": self.valid_from.isoformat() if self.valid_from else None,
            "valid_until": self.valid_until.isoformat() if self.valid_until else None,
            "total_amount": float(self.calculate_total_amount()),
            "notes": self.notes,
            "metadata": self.metadata,
        }


class OfferHandler:
    """Handler for managing payment offers and terms."""
    
    def __init__(self):
        """Initialize offer handler."""
        self.offers: Dict[str, PaymentOffer] = {}
        self.offer_history: List[Dict[str, Any]] = []
    
    def create_offer(
        self,
        offer_id: str,
        customer_id: str,
        amount: Decimal,
        offer_type: OfferType = OfferType.STANDARD,
        currency: str = "USD",
        terms: Optional[PaymentTerms] = None,
        discount_percentage: Optional[Decimal] = None,
        discount_amount: Optional[Decimal] = None,
        valid_days: Optional[int] = None,
        description: Optional[str] = None,
        notes: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> PaymentOffer:
        """
        Create a new payment offer.
        
        Args:
            offer_id: Unique identifier for the offer
            customer_id: ID of the customer
            amount: Base amount for the offer
            offer_type: Type of offer
            currency: Currency code
            terms: Payment terms
            discount_percentage: Discount percentage (0-100)
            discount_amount: Discount amount
            valid_days: Number of days the offer is valid
            description: Offer description
            notes: Additional notes
            metadata: Additional metadata
        
        Returns:
            PaymentOffer: The created offer
        """
        if offer_id in self.offers:
            raise ValueError(f"Offer with ID {offer_id} already exists")
        
        now = datetime.utcnow()
        valid_until = None
        if valid_days:
            valid_until = now + timedelta(days=valid_days)
        
        offer = PaymentOffer(
            offer_id=offer_id,
            customer_id=customer_id,
            amount=amount,
            currency=currency,
            offer_type=offer_type,
            status=OfferStatus.DRAFT,
            terms=terms,
            discount_percentage=discount_percentage,
            discount_amount=discount_amount,
            created_at=now,
            valid_until=valid_until,
            description=description,
            notes=notes,
            metadata=metadata or {},
        )
        
        self.offers[offer_id] = offer
        self._log_offer_event(offer, "created")
        
        return offer
    
    def update_offer(
        self,
        offer_id: str,
        **kwargs
    ) -> PaymentOffer:
        """
        Update an existing offer.
        
        Args:
            offer_id: ID of the offer to update
            **kwargs: Fields to update
        
        Returns:
            PaymentOffer: The updated offer
        """
        if offer_id not in self.offers:
            raise ValueError(f"Offer with ID {offer_id} not found")
        
        offer = self.offers[offer_id]
        
        for key, value in kwargs.items():
            if hasattr(offer, key):
                setattr(offer, key, value)
        
        self._log_offer_event(offer, "updated")
        
        return offer
    
    def approve_offer(self, offer_id: str) -> PaymentOffer:
        """
        Approve a pending offer.
        
        Args:
            offer_id: ID of the offer to approve
        
        Returns:
            PaymentOffer: The approved offer
        """
        if offer_id not in self.offers:
            raise ValueError(f"Offer with ID {offer_id} not found")
        
        offer = self.offers[offer_id]
        offer.status = OfferStatus.APPROVED
        
        self._log_offer_event(offer, "approved")
        
        return offer
    
    def activate_offer(self, offer_id: str) -> PaymentOffer:
        """
        Activate an offer.
        
        Args:
            offer_id: ID of the offer to activate
        
        Returns:
            PaymentOffer: The activated offer
        """
        if offer_id not in self.offers:
            raise ValueError(f"Offer with ID {offer_id} not found")
        
        offer = self.offers[offer_id]
        offer.status = OfferStatus.ACTIVE
        if not offer.valid_from:
            offer.valid_from = datetime.utcnow()
        
        self._log_offer_event(offer, "activated")
        
        return offer
    
    def accept_offer(self, offer_id: str) -> PaymentOffer:
        """
        Mark an offer as accepted by the customer.
        
        Args:
            offer_id: ID of the offer to accept
        
        Returns:
            PaymentOffer: The accepted offer
        """
        if offer_id not in self.offers:
            raise ValueError(f"Offer with ID {offer_id} not found")
        
        offer = self.offers[offer_id]
        offer.status = OfferStatus.ACCEPTED
        
        self._log_offer_event(offer, "accepted")
        
        return offer
    
    def cancel_offer(self, offer_id: str, reason: Optional[str] = None) -> PaymentOffer:
        """
        Cancel an offer.
        
        Args:
            offer_id: ID of the offer to cancel
            reason: Reason for cancellation
        
        Returns:
            PaymentOffer: The cancelled offer
        """
        if offer_id not in self.offers:
            raise ValueError(f"Offer with ID {offer_id} not found")
        
        offer = self.offers[offer_id]
        offer.status = OfferStatus.CANCELLED
        if reason:
            offer.notes = f"Cancelled: {reason}"
        
        self._log_offer_event(offer, "cancelled")
        
        return offer
    
    def get_offer(self, offer_id: str) -> Optional[PaymentOffer]:
        """
        Get an offer by ID.
        
        Args:
            offer_id: ID of the offer
        
        Returns:
            PaymentOffer or None if not found
        """
        return self.offers.get(offer_id)
    
    def get_customer_offers(
        self,
        customer_id: str,
        status: Optional[OfferStatus] = None,
        active_only: bool = False
    ) -> List[PaymentOffer]:
        """
        Get all offers for a customer.
        
        Args:
            customer_id: ID of the customer
            status: Filter by status
            active_only: Return only active offers
        
        Returns:
            List of offers
        """
        offers = [
            offer for offer in self.offers.values()
            if offer.customer_id == customer_id
        ]
        
        if status:
            offers = [o for o in offers if o.status == status]
        
        if active_only:
            offers = [o for o in offers if o.is_active()]
        
        return offers
    
    def get_offer_history(self, offer_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get offer history.
        
        Args:
            offer_id: Filter by offer ID (optional)
        
        Returns:
            List of history events
        """
        if offer_id:
            return [e for e in self.offer_history if e.get("offer_id") == offer_id]
        return self.offer_history
    
    def _log_offer_event(self, offer: PaymentOffer, event_type: str) -> None:
        """
        Log an offer event to history.
        
        Args:
            offer: The offer
            event_type: Type of event
        """
        self.offer_history.append({
            "offer_id": offer.offer_id,
            "customer_id": offer.customer_id,
            "event_type": event_type,
            "status": offer.status.value,
            "timestamp": datetime.utcnow().isoformat(),
            "amount": float(offer.amount),
        })
    
    def export_offer(self, offer_id: str) -> str:
        """
        Export offer as JSON string.
        
        Args:
            offer_id: ID of the offer
        
        Returns:
            JSON string representation of the offer
        """
        offer = self.get_offer(offer_id)
        if not offer:
            raise ValueError(f"Offer with ID {offer_id} not found")
        
        return json.dumps(offer.to_dict(), indent=2)


# Default payment terms presets
DEFAULT_TERMS = {
    TermsType.IMMEDIATE: PaymentTerms(
        terms_type=TermsType.IMMEDIATE,
        days_until_due=0,
    ),
    TermsType.NET_30: PaymentTerms(
        terms_type=TermsType.NET_30,
        days_until_due=30,
        early_payment_discount=Decimal(2),  # 2% discount for early payment
    ),
    TermsType.NET_60: PaymentTerms(
        terms_type=TermsType.NET_60,
        days_until_due=60,
        early_payment_discount=Decimal(1),
    ),
    TermsType.NET_90: PaymentTerms(
        terms_type=TermsType.NET_90,
        days_until_due=90,
    ),
}
