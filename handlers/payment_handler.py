"""
Payment Handler Module

Comprehensive payment processing logic including:
- Offer display and management
- SBP (System for Transfers Between Banks) payment flow
- Payment validation and error handling
- Transaction tracking and logging
"""

import logging
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
from datetime import datetime, timedelta
from decimal import Decimal
import json

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class PaymentStatus(Enum):
    """Payment status enumeration"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(Enum):
    """Available payment methods"""
    SBP = "sbp"  # System for Transfers Between Banks
    CARD = "card"
    WALLET = "wallet"
    BANK_TRANSFER = "bank_transfer"


class OfferType(Enum):
    """Types of offers available"""
    DISCOUNT = "discount"
    CASHBACK = "cashback"
    BONUS = "bonus"
    FREE_SHIPPING = "free_shipping"
    LOYALTY_POINTS = "loyalty_points"


@dataclass
class Offer:
    """Data class representing an offer"""
    id: str
    type: OfferType
    title: str
    description: str
    discount_percentage: Optional[float] = None
    cashback_amount: Optional[Decimal] = None
    bonus_points: Optional[int] = None
    min_amount: Decimal = Decimal("0.00")
    max_discount: Optional[Decimal] = None
    valid_from: datetime = None
    valid_until: datetime = None
    code: Optional[str] = None
    is_active: bool = True
    usage_limit: Optional[int] = None
    current_usage: int = 0

    def is_valid(self) -> bool:
        """Check if offer is currently valid"""
        now = datetime.utcnow()
        if not self.is_active:
            return False
        if self.valid_from and now < self.valid_from:
            return False
        if self.valid_until and now > self.valid_until:
            return False
        if self.usage_limit and self.current_usage >= self.usage_limit:
            return False
        return True

    def calculate_discount(self, amount: Decimal) -> Decimal:
        """Calculate discount amount based on offer type"""
        if not self.is_valid():
            return Decimal("0.00")

        if amount < self.min_amount:
            return Decimal("0.00")

        if self.type == OfferType.DISCOUNT and self.discount_percentage:
            discount = amount * Decimal(str(self.discount_percentage / 100))
            if self.max_discount:
                discount = min(discount, self.max_discount)
            return discount

        if self.type == OfferType.CASHBACK and self.cashback_amount:
            return min(self.cashback_amount, amount)

        return Decimal("0.00")


@dataclass
class PaymentOffer:
    """Combined payment offer data"""
    offer: Offer
    applied_discount: Decimal
    points_earned: int = 0


@dataclass
class Transaction:
    """Data class representing a transaction"""
    id: str
    user_id: str
    amount: Decimal
    currency: str
    payment_method: PaymentMethod
    status: PaymentStatus
    created_at: datetime
    updated_at: datetime
    description: Optional[str] = None
    order_id: Optional[str] = None
    applied_offers: List[PaymentOffer] = None
    total_discount: Decimal = Decimal("0.00")
    final_amount: Decimal = None
    sbp_details: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.applied_offers is None:
            self.applied_offers = []
        if self.metadata is None:
            self.metadata = {}
        if self.final_amount is None:
            self.final_amount = self.amount - self.total_discount

    def to_dict(self) -> Dict:
        """Convert transaction to dictionary"""
        data = asdict(self)
        data['amount'] = str(self.amount)
        data['total_discount'] = str(self.total_discount)
        data['final_amount'] = str(self.final_amount)
        data['payment_method'] = self.payment_method.value
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        data['updated_at'] = self.updated_at.isoformat()
        return data


class OfferManager:
    """Manages offers and discount application"""

    def __init__(self):
        self.offers: Dict[str, Offer] = {}
        self._initialize_default_offers()

    def _initialize_default_offers(self):
        """Initialize default offers"""
        default_offers = [
            Offer(
                id="offer_001",
                type=OfferType.DISCOUNT,
                title="Welcome Discount",
                description="10% discount on first purchase",
                discount_percentage=10,
                max_discount=Decimal("50.00"),
                min_amount=Decimal("10.00"),
                valid_from=datetime.utcnow(),
                valid_until=datetime.utcnow() + timedelta(days=30),
                code="WELCOME10"
            ),
            Offer(
                id="offer_002",
                type=OfferType.CASHBACK,
                title="Cashback Offer",
                description="Get 5% cashback",
                cashback_amount=Decimal("5.00"),
                min_amount=Decimal("50.00"),
                valid_from=datetime.utcnow(),
                valid_until=datetime.utcnow() + timedelta(days=90),
                code="CASHBACK5"
            ),
            Offer(
                id="offer_003",
                type=OfferType.FREE_SHIPPING,
                title="Free Shipping",
                description="Free shipping on orders over 500",
                min_amount=Decimal("500.00"),
                valid_from=datetime.utcnow(),
                valid_until=datetime.utcnow() + timedelta(days=60)
            )
        ]

        for offer in default_offers:
            self.offers[offer.id] = offer

    def add_offer(self, offer: Offer) -> bool:
        """Add a new offer"""
        if offer.id in self.offers:
            logger.warning(f"Offer {offer.id} already exists")
            return False
        self.offers[offer.id] = offer
        logger.info(f"Offer {offer.id} added successfully")
        return True

    def get_available_offers(self, amount: Decimal) -> List[Offer]:
        """Get all available offers for a given amount"""
        available = []
        for offer in self.offers.values():
            if offer.is_valid() and amount >= offer.min_amount:
                available.append(offer)
        return available

    def apply_offers(self, amount: Decimal, offer_ids: List[str] = None) -> Tuple[Decimal, List[PaymentOffer]]:
        """
        Apply offers to an amount
        
        Args:
            amount: Base transaction amount
            offer_ids: Specific offer IDs to apply (optional)
        
        Returns:
            Tuple of (total_discount, applied_offers_list)
        """
        applied_offers = []
        total_discount = Decimal("0.00")

        if offer_ids is None:
            offer_ids = []

        # Get offers to apply
        offers_to_apply = []
        if offer_ids:
            for offer_id in offer_ids:
                if offer_id in self.offers:
                    offers_to_apply.append(self.offers[offer_id])
        else:
            offers_to_apply = self.get_available_offers(amount)

        # Apply each offer
        for offer in offers_to_apply:
            if offer.is_valid():
                discount = offer.calculate_discount(amount - total_discount)
                if discount > 0:
                    offer.current_usage += 1
                    payment_offer = PaymentOffer(
                        offer=offer,
                        applied_discount=discount,
                        points_earned=offer.bonus_points or 0
                    )
                    applied_offers.append(payment_offer)
                    total_discount += discount

        logger.info(f"Applied {len(applied_offers)} offers, total discount: {total_discount}")
        return total_discount, applied_offers

    def get_offer_details(self, offer_id: str) -> Optional[Offer]:
        """Get details of a specific offer"""
        return self.offers.get(offer_id)


class SBPPaymentProcessor:
    """Handles SBP (System for Transfers Between Banks) payment processing"""

    def __init__(self):
        self.sbp_endpoint = "https://sbp.example.com/api"  # Placeholder URL
        self.timeout = 30
        self.retry_count = 3

    def validate_sbp_details(self, sbp_details: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate SBP payment details
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        required_fields = ["phone", "bank_code", "account_number"]
        
        for field in required_fields:
            if field not in sbp_details:
                return False, f"Missing required field: {field}"

        phone = sbp_details.get("phone", "")
        if not self._validate_phone(phone):
            return False, "Invalid phone number format"

        bank_code = sbp_details.get("bank_code", "")
        if not self._validate_bank_code(bank_code):
            return False, "Invalid bank code"

        return True, ""

    def _validate_phone(self, phone: str) -> bool:
        """Validate phone number format"""
        # Russian phone format validation (example)
        import re
        pattern = r'^\+?7\d{10}$'
        return bool(re.match(pattern, phone.replace(" ", "").replace("-", "")))

    def _validate_bank_code(self, bank_code: str) -> bool:
        """Validate bank code"""
        # Simple validation - should be 4-5 digit code
        return bank_code.isdigit() and 4 <= len(bank_code) <= 5

    def initiate_payment(self, transaction: Transaction) -> Tuple[bool, str, Optional[Dict]]:
        """
        Initiate SBP payment
        
        Returns:
            Tuple of (success, message, payment_reference)
        """
        is_valid, error_msg = self.validate_sbp_details(transaction.sbp_details)
        if not is_valid:
            logger.error(f"SBP validation failed: {error_msg}")
            return False, error_msg, None

        try:
            payment_ref = self._generate_payment_reference()
            
            # Simulate API call
            payload = {
                "reference": payment_ref,
                "amount": str(transaction.final_amount),
                "currency": transaction.currency,
                "phone": transaction.sbp_details.get("phone"),
                "bank_code": transaction.sbp_details.get("bank_code"),
                "description": transaction.description,
                "order_id": transaction.order_id
            }

            logger.info(f"Initiating SBP payment: {payment_ref}")
            
            # In production, this would be an actual API call
            response = self._simulate_sbp_api_call(payload)
            
            if response.get("status") == "success":
                return True, "Payment initiated successfully", {
                    "payment_reference": payment_ref,
                    "timestamp": datetime.utcnow().isoformat(),
                    "status": "pending"
                }
            else:
                return False, response.get("error", "Unknown error"), None

        except Exception as e:
            logger.error(f"Error initiating SBP payment: {str(e)}")
            return False, f"Payment initiation failed: {str(e)}", None

    def _generate_payment_reference(self) -> str:
        """Generate unique payment reference"""
        import uuid
        return f"SBP_{uuid.uuid4().hex[:12].upper()}"

    def _simulate_sbp_api_call(self, payload: Dict) -> Dict:
        """Simulate SBP API call (replace with real API in production)"""
        # This is a simulation for testing
        return {
            "status": "success",
            "reference": payload.get("reference"),
            "timestamp": datetime.utcnow().isoformat()
        }

    def verify_payment(self, payment_reference: str) -> Tuple[bool, Optional[Dict]]:
        """Verify SBP payment status"""
        try:
            # In production, this would query the SBP system
            logger.info(f"Verifying payment: {payment_reference}")
            
            return True, {
                "payment_reference": payment_reference,
                "status": "completed",
                "verified_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Error verifying payment: {str(e)}")
            return False, None


class PaymentProcessor:
    """Main payment processor orchestrating all payment operations"""

    def __init__(self):
        self.offer_manager = OfferManager()
        self.sbp_processor = SBPPaymentProcessor()
        self.transactions: Dict[str, Transaction] = {}
        self.transaction_counter = 0

    def create_transaction(
        self,
        user_id: str,
        amount: Decimal,
        currency: str = "RUB",
        payment_method: PaymentMethod = PaymentMethod.SBP,
        description: Optional[str] = None,
        order_id: Optional[str] = None,
        offer_ids: Optional[List[str]] = None,
        sbp_details: Optional[Dict] = None
    ) -> Transaction:
        """Create a new transaction"""
        self.transaction_counter += 1
        transaction_id = f"TXN_{datetime.utcnow().strftime('%Y%m%d')}_{self.transaction_counter:06d}"

        # Apply offers
        total_discount, applied_offers = self.offer_manager.apply_offers(amount, offer_ids)
        final_amount = amount - total_discount

        transaction = Transaction(
            id=transaction_id,
            user_id=user_id,
            amount=amount,
            currency=currency,
            payment_method=payment_method,
            status=PaymentStatus.PENDING,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
            description=description,
            order_id=order_id,
            applied_offers=applied_offers,
            total_discount=total_discount,
            final_amount=final_amount,
            sbp_details=sbp_details or {}
        )

        self.transactions[transaction_id] = transaction
        logger.info(f"Created transaction: {transaction_id}")
        return transaction

    def process_payment(self, transaction_id: str) -> Tuple[bool, str, Optional[Dict]]:
        """Process payment for a transaction"""
        if transaction_id not in self.transactions:
            return False, "Transaction not found", None

        transaction = self.transactions[transaction_id]

        if transaction.status != PaymentStatus.PENDING:
            return False, f"Transaction is {transaction.status.value}", None

        # Update status
        transaction.status = PaymentStatus.PROCESSING
        transaction.updated_at = datetime.utcnow()

        try:
            if transaction.payment_method == PaymentMethod.SBP:
                success, message, sbp_response = self.sbp_processor.initiate_payment(transaction)
                
                if success:
                    transaction.status = PaymentStatus.COMPLETED
                    transaction.sbp_details.update(sbp_response or {})
                    logger.info(f"Payment processed successfully: {transaction_id}")
                    return True, "Payment processed successfully", sbp_response
                else:
                    transaction.status = PaymentStatus.FAILED
                    logger.error(f"Payment failed: {message}")
                    return False, message, None
            else:
                # Handle other payment methods
                transaction.status = PaymentStatus.COMPLETED
                logger.info(f"Payment processed via {transaction.payment_method.value}: {transaction_id}")
                return True, "Payment processed successfully", None

        except Exception as e:
            transaction.status = PaymentStatus.FAILED
            logger.error(f"Error processing payment: {str(e)}")
            return False, f"Payment processing error: {str(e)}", None
        finally:
            transaction.updated_at = datetime.utcnow()

    def get_transaction(self, transaction_id: str) -> Optional[Transaction]:
        """Get transaction details"""
        return self.transactions.get(transaction_id)

    def refund_transaction(self, transaction_id: str, reason: str = "") -> Tuple[bool, str]:
        """Refund a completed transaction"""
        if transaction_id not in self.transactions:
            return False, "Transaction not found"

        transaction = self.transactions[transaction_id]

        if transaction.status != PaymentStatus.COMPLETED:
            return False, f"Cannot refund transaction in {transaction.status.value} state"

        try:
            transaction.status = PaymentStatus.REFUNDED
            transaction.updated_at = datetime.utcnow()
            transaction.metadata['refund_reason'] = reason
            transaction.metadata['refunded_at'] = datetime.utcnow().isoformat()

            logger.info(f"Transaction refunded: {transaction_id}")
            return True, "Refund processed successfully"

        except Exception as e:
            logger.error(f"Error refunding transaction: {str(e)}")
            return False, f"Refund failed: {str(e)}"

    def display_offers(self, amount: Decimal) -> List[Dict]:
        """Display available offers for a given amount"""
        offers = self.offer_manager.get_available_offers(amount)
        
        offer_list = []
        for offer in offers:
            discount = offer.calculate_discount(amount)
            offer_list.append({
                "id": offer.id,
                "title": offer.title,
                "description": offer.description,
                "type": offer.type.value,
                "discount_amount": str(discount),
                "code": offer.code,
                "valid_until": offer.valid_until.isoformat() if offer.valid_until else None
            })

        logger.info(f"Displayed {len(offer_list)} offers for amount {amount}")
        return offer_list

    def get_payment_summary(self, transaction_id: str) -> Optional[Dict]:
        """Get detailed payment summary"""
        transaction = self.get_transaction(transaction_id)
        if not transaction:
            return None

        summary = {
            "transaction_id": transaction.id,
            "user_id": transaction.user_id,
            "original_amount": str(transaction.amount),
            "currency": transaction.currency,
            "applied_offers": [
                {
                    "offer_id": po.offer.id,
                    "title": po.offer.title,
                    "discount": str(po.applied_discount),
                    "points_earned": po.points_earned
                }
                for po in transaction.applied_offers
            ],
            "total_discount": str(transaction.total_discount),
            "final_amount": str(transaction.final_amount),
            "payment_method": transaction.payment_method.value,
            "status": transaction.status.value,
            "created_at": transaction.created_at.isoformat(),
            "updated_at": transaction.updated_at.isoformat(),
            "order_id": transaction.order_id
        }

        return summary
