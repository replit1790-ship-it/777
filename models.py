"""
Data models for the application.
"""
from datetime import datetime
from typing import Optional, List


class User:
    """User model representing a user in the system."""
    
    def __init__(self, user_id: str, username: str, email: str, created_at: Optional[datetime] = None):
        self.user_id = user_id
        self.username = username
        self.email = email
        self.created_at = created_at or datetime.utcnow()
        self.is_active = True
    
    def __repr__(self) -> str:
        return f"User(user_id={self.user_id}, username={self.username}, email={self.email})"


class Order:
    """Order model representing a customer order."""
    
    def __init__(self, order_id: str, user_id: str, total_amount: float, status: str = "pending"):
        self.order_id = order_id
        self.user_id = user_id
        self.total_amount = total_amount
        self.status = status
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
        self.items = []
    
    def add_item(self, item: dict) -> None:
        """Add an item to the order."""
        self.items.append(item)
        self.updated_at = datetime.utcnow()
    
    def update_status(self, new_status: str) -> None:
        """Update the order status."""
        self.status = new_status
        self.updated_at = datetime.utcnow()
    
    def __repr__(self) -> str:
        return f"Order(order_id={self.order_id}, user_id={self.user_id}, status={self.status}, total_amount={self.total_amount})"


class Payment:
    """Payment model representing a payment transaction."""
    
    def __init__(self, payment_id: str, order_id: str, amount: float, payment_method: str, status: str = "pending"):
        self.payment_id = payment_id
        self.order_id = order_id
        self.amount = amount
        self.payment_method = payment_method
        self.status = status
        self.created_at = datetime.utcnow()
        self.processed_at: Optional[datetime] = None
    
    def mark_as_processed(self) -> None:
        """Mark the payment as processed."""
        self.status = "processed"
        self.processed_at = datetime.utcnow()
    
    def mark_as_failed(self) -> None:
        """Mark the payment as failed."""
        self.status = "failed"
    
    def __repr__(self) -> str:
        return f"Payment(payment_id={self.payment_id}, order_id={self.order_id}, amount={self.amount}, status={self.status})"


class Transaction:
    """Transaction model representing a financial transaction."""
    
    def __init__(self, transaction_id: str, payment_id: str, transaction_type: str, amount: float, 
                 reference: str = ""):
        self.transaction_id = transaction_id
        self.payment_id = payment_id
        self.transaction_type = transaction_type  # e.g., 'debit', 'credit'
        self.amount = amount
        self.reference = reference
        self.status = "pending"
        self.created_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None
    
    def mark_as_completed(self) -> None:
        """Mark the transaction as completed."""
        self.status = "completed"
        self.completed_at = datetime.utcnow()
    
    def mark_as_failed(self) -> None:
        """Mark the transaction as failed."""
        self.status = "failed"
    
    def __repr__(self) -> str:
        return f"Transaction(transaction_id={self.transaction_id}, payment_id={self.payment_id}, " \
               f"type={self.transaction_type}, amount={self.amount}, status={self.status})"
