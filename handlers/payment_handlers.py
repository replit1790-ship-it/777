"""
Payment Processing Handlers

This module provides payment processing functionality including:
- Payment validation
- Transaction processing
- Payment gateway integration
- Order fulfillment
"""

import logging
from typing import Dict, Optional, Tuple, Any
from datetime import datetime
from enum import Enum
import json

# Configure logging
logger = logging.getLogger(__name__)


class PaymentStatus(Enum):
    """Enumeration of payment statuses"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class PaymentMethod(Enum):
    """Enumeration of supported payment methods"""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    BANK_TRANSFER = "bank_transfer"
    CRYPTOCURRENCY = "cryptocurrency"


class PaymentHandler:
    """Main payment handler class for processing transactions"""
    
    def __init__(self):
        """Initialize payment handler"""
        self.transactions: Dict[str, Dict[str, Any]] = {}
        self.logger = logger
    
    def validate_payment_details(
        self,
        amount: float,
        currency: str,
        payment_method: PaymentMethod,
        customer_id: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate payment details before processing
        
        Args:
            amount: Transaction amount
            currency: Currency code (e.g., 'USD')
            payment_method: Payment method enum
            customer_id: Customer identifier
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if amount <= 0:
            return False, "Amount must be greater than zero"
        
        if not isinstance(amount, (int, float)):
            return False, "Invalid amount type"
        
        if not currency or len(currency) != 3:
            return False, "Invalid currency code"
        
        if not customer_id or not isinstance(customer_id, str):
            return False, "Invalid customer ID"
        
        if not isinstance(payment_method, PaymentMethod):
            return False, "Invalid payment method"
        
        self.logger.info(
            f"Payment details validated - Amount: {amount} {currency}, "
            f"Method: {payment_method.value}, Customer: {customer_id}"
        )
        return True, None
    
    def process_payment(
        self,
        transaction_id: str,
        amount: float,
        currency: str,
        payment_method: PaymentMethod,
        customer_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process a payment transaction
        
        Args:
            transaction_id: Unique transaction identifier
            amount: Transaction amount
            currency: Currency code
            payment_method: Payment method
            customer_id: Customer identifier
            metadata: Additional metadata
            
        Returns:
            Transaction result dictionary
        """
        # Validate payment details
        is_valid, error = self.validate_payment_details(
            amount, currency, payment_method, customer_id
        )
        
        if not is_valid:
            return {
                "success": False,
                "transaction_id": transaction_id,
                "status": PaymentStatus.FAILED.value,
                "error": error,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        # Store transaction
        transaction = {
            "transaction_id": transaction_id,
            "amount": amount,
            "currency": currency,
            "payment_method": payment_method.value,
            "customer_id": customer_id,
            "status": PaymentStatus.PROCESSING.value,
            "created_at": datetime.utcnow().isoformat(),
            "metadata": metadata or {}
        }
        
        self.transactions[transaction_id] = transaction
        
        try:
            # Process payment through gateway
            result = self._process_through_gateway(transaction)
            
            if result["success"]:
                transaction["status"] = PaymentStatus.COMPLETED.value
                self.logger.info(f"Payment processed successfully: {transaction_id}")
            else:
                transaction["status"] = PaymentStatus.FAILED.value
                self.logger.warning(f"Payment processing failed: {transaction_id}")
            
            transaction["completed_at"] = datetime.utcnow().isoformat()
            return result
            
        except Exception as e:
            self.logger.error(f"Error processing payment {transaction_id}: {str(e)}")
            transaction["status"] = PaymentStatus.FAILED.value
            transaction["error"] = str(e)
            return {
                "success": False,
                "transaction_id": transaction_id,
                "status": PaymentStatus.FAILED.value,
                "error": f"Payment processing error: {str(e)}",
                "timestamp": datetime.utcnow().isoformat()
            }
    
    def _process_through_gateway(self, transaction: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process transaction through payment gateway
        
        Args:
            transaction: Transaction details
            
        Returns:
            Gateway response
        """
        # Simulate gateway processing
        self.logger.info(f"Processing transaction through gateway: {transaction['transaction_id']}")
        
        # In production, this would call actual payment gateway API
        return {
            "success": True,
            "transaction_id": transaction["transaction_id"],
            "status": PaymentStatus.COMPLETED.value,
            "amount": transaction["amount"],
            "currency": transaction["currency"],
            "payment_method": transaction["payment_method"],
            "customer_id": transaction["customer_id"],
            "gateway_reference": f"GW_{transaction['transaction_id'][:8]}_REF",
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def refund_payment(
        self,
        transaction_id: str,
        refund_amount: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Refund a completed payment
        
        Args:
            transaction_id: Original transaction identifier
            refund_amount: Amount to refund (None for full refund)
            
        Returns:
            Refund result
        """
        if transaction_id not in self.transactions:
            return {
                "success": False,
                "error": f"Transaction {transaction_id} not found",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        transaction = self.transactions[transaction_id]
        
        if transaction["status"] != PaymentStatus.COMPLETED.value:
            return {
                "success": False,
                "error": f"Cannot refund transaction with status: {transaction['status']}",
                "transaction_id": transaction_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        refund_amt = refund_amount or transaction["amount"]
        
        if refund_amt > transaction["amount"]:
            return {
                "success": False,
                "error": "Refund amount exceeds original transaction amount",
                "transaction_id": transaction_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        refund_id = f"REF_{transaction_id}"
        transaction["status"] = PaymentStatus.REFUNDED.value
        transaction["refund_amount"] = refund_amt
        transaction["refund_id"] = refund_id
        transaction["refunded_at"] = datetime.utcnow().isoformat()
        
        self.logger.info(f"Payment refunded: {transaction_id}, Amount: {refund_amt}")
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "refund_id": refund_id,
            "refund_amount": refund_amt,
            "status": PaymentStatus.REFUNDED.value,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_transaction_status(self, transaction_id: str) -> Dict[str, Any]:
        """
        Get the status of a transaction
        
        Args:
            transaction_id: Transaction identifier
            
        Returns:
            Transaction status information
        """
        if transaction_id not in self.transactions:
            return {
                "success": False,
                "error": f"Transaction {transaction_id} not found",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        transaction = self.transactions[transaction_id]
        return {
            "success": True,
            "transaction_id": transaction_id,
            "status": transaction["status"],
            "amount": transaction["amount"],
            "currency": transaction["currency"],
            "customer_id": transaction["customer_id"],
            "created_at": transaction["created_at"],
            "completed_at": transaction.get("completed_at"),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def cancel_payment(self, transaction_id: str) -> Dict[str, Any]:
        """
        Cancel a pending payment
        
        Args:
            transaction_id: Transaction identifier
            
        Returns:
            Cancellation result
        """
        if transaction_id not in self.transactions:
            return {
                "success": False,
                "error": f"Transaction {transaction_id} not found",
                "timestamp": datetime.utcnow().isoformat()
            }
        
        transaction = self.transactions[transaction_id]
        
        if transaction["status"] not in [PaymentStatus.PENDING.value, PaymentStatus.PROCESSING.value]:
            return {
                "success": False,
                "error": f"Cannot cancel transaction with status: {transaction['status']}",
                "transaction_id": transaction_id,
                "timestamp": datetime.utcnow().isoformat()
            }
        
        transaction["status"] = PaymentStatus.CANCELLED.value
        transaction["cancelled_at"] = datetime.utcnow().isoformat()
        
        self.logger.info(f"Payment cancelled: {transaction_id}")
        
        return {
            "success": True,
            "transaction_id": transaction_id,
            "status": PaymentStatus.CANCELLED.value,
            "timestamp": datetime.utcnow().isoformat()
        }
    
    def get_transaction_history(self, customer_id: str) -> Dict[str, Any]:
        """
        Get transaction history for a customer
        
        Args:
            customer_id: Customer identifier
            
        Returns:
            List of transactions for the customer
        """
        customer_transactions = [
            txn for txn in self.transactions.values()
            if txn["customer_id"] == customer_id
        ]
        
        return {
            "success": True,
            "customer_id": customer_id,
            "transaction_count": len(customer_transactions),
            "transactions": customer_transactions,
            "timestamp": datetime.utcnow().isoformat()
        }


# Initialize global payment handler
payment_handler = PaymentHandler()


def handle_payment_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Handle incoming payment request
    
    Args:
        request_data: Payment request data
        
    Returns:
        Payment response
    """
    try:
        return payment_handler.process_payment(
            transaction_id=request_data.get("transaction_id"),
            amount=request_data.get("amount"),
            currency=request_data.get("currency", "USD"),
            payment_method=PaymentMethod(request_data.get("payment_method")),
            customer_id=request_data.get("customer_id"),
            metadata=request_data.get("metadata")
        )
    except Exception as e:
        logger.error(f"Error handling payment request: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }
