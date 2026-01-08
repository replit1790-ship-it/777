"""
Robokassa SBP Payment Integration Handler

This module provides integration with Robokassa payment gateway for SBP (System for Payment by Bank Accounts) payments.
It handles payment initialization, verification, and webhook processing.
"""

import hashlib
import hmac
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, Any
from datetime import datetime
from urllib.parse import urlencode

import requests

logger = logging.getLogger(__name__)


class PaymentStatus(Enum):
    """Robokassa payment status codes."""
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    CANCELLED = "cancelled"
    EXPIRED = "expired"


@dataclass
class RobokassaConfig:
    """Configuration for Robokassa payment gateway."""
    merchant_id: str
    password1: str
    password2: str
    test_mode: bool = False
    
    @property
    def base_url(self) -> str:
        """Get the base URL for Robokassa API."""
        if self.test_mode:
            return "https://test.robokassa.ru"
        return "https://auth.robokassa.ru"


class RobokassaHandler:
    """
    Handler for Robokassa SBP payment integration.
    
    This class manages payment initialization, signature verification,
    and webhook processing for Robokassa payments.
    """
    
    def __init__(self, config: RobokassaConfig):
        """
        Initialize the Robokassa payment handler.
        
        Args:
            config: RobokassaConfig instance with merchant credentials
        """
        self.config = config
        self.session = requests.Session()
    
    def _generate_signature(self, 
                           merchant_id: str,
                           amount: float,
                           order_id: str,
                           password: str,
                           extra_params: Optional[Dict[str, str]] = None) -> str:
        """
        Generate MD5 signature for Robokassa payment request.
        
        Args:
            merchant_id: Merchant ID
            amount: Payment amount in rubles
            order_id: Unique order identifier
            password: Password for signature generation (password1 or password2)
            extra_params: Additional parameters to include in signature
            
        Returns:
            MD5 hash signature
        """
        signature_parts = [merchant_id, str(amount), order_id]
        
        if extra_params:
            # Add extra parameters in sorted order
            for key in sorted(extra_params.keys()):
                signature_parts.append(f"{key}={extra_params[key]}")
        
        signature_parts.append(password)
        
        signature_str = ":".join(signature_parts)
        signature = hashlib.md5(signature_str.encode()).hexdigest()
        
        logger.debug(f"Generated signature for order {order_id}: {signature}")
        return signature
    
    def _verify_signature(self,
                         merchant_id: str,
                         amount: float,
                         order_id: str,
                         provided_signature: str,
                         extra_params: Optional[Dict[str, str]] = None) -> bool:
        """
        Verify signature from Robokassa webhook.
        
        Args:
            merchant_id: Merchant ID
            amount: Payment amount in rubles
            order_id: Order identifier
            provided_signature: Signature provided by Robokassa
            extra_params: Additional parameters included in signature
            
        Returns:
            True if signature is valid, False otherwise
        """
        # Try with password2 first (used for payment confirmation)
        expected_signature = self._generate_signature(
            merchant_id, amount, order_id, self.config.password2, extra_params
        )
        
        if hmac.compare_digest(provided_signature, expected_signature):
            logger.info(f"Signature verified successfully for order {order_id}")
            return True
        
        # Fall back to password1 for backwards compatibility
        expected_signature = self._generate_signature(
            merchant_id, amount, order_id, self.config.password1, extra_params
        )
        
        if hmac.compare_digest(provided_signature, expected_signature):
            logger.info(f"Signature verified with password1 for order {order_id}")
            return True
        
        logger.warning(f"Signature verification failed for order {order_id}")
        return False
    
    def create_payment_url(self,
                          amount: float,
                          order_id: str,
                          description: str,
                          email: str = "",
                          phone: str = "",
                          extra_params: Optional[Dict[str, str]] = None) -> str:
        """
        Create a payment URL for redirecting user to Robokassa.
        
        Args:
            amount: Payment amount in rubles
            order_id: Unique order identifier
            description: Payment description
            email: Customer email (optional)
            phone: Customer phone number (optional)
            extra_params: Additional parameters to pass to Robokassa
            
        Returns:
            Complete payment URL for user redirect
        """
        params = {
            "MerchantLogin": self.config.merchant_id,
            "Sum": str(round(amount, 2)),
            "InvId": str(order_id),
            "Description": description,
            "IsTest": "1" if self.config.test_mode else "0",
        }
        
        # Add optional parameters
        if email:
            params["Email"] = email
        if phone:
            params["Phone"] = phone
        
        # Add extra parameters
        extra_params = extra_params or {}
        params.update(extra_params)
        
        # Generate signature
        signature = self._generate_signature(
            self.config.merchant_id,
            amount,
            order_id,
            self.config.password1,
            extra_params if extra_params else None
        )
        params["SignatureValue"] = signature
        
        # Build URL
        payment_url = f"{self.config.base_url}/Basket.aspx"
        full_url = f"{payment_url}?{urlencode(params)}"
        
        logger.info(f"Created payment URL for order {order_id}: {payment_url}")
        return full_url
    
    def process_webhook(self, webhook_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process webhook from Robokassa payment notification.
        
        Args:
            webhook_data: Dictionary containing webhook data from Robokassa
            
        Returns:
            Dictionary with processing result containing:
                - success: bool indicating successful processing
                - order_id: str order identifier
                - status: PaymentStatus
                - amount: float payment amount
                - message: str processing message
        """
        try:
            # Extract webhook parameters
            order_id = str(webhook_data.get("InvId"))
            amount = float(webhook_data.get("Sum", 0))
            signature = webhook_data.get("SignatureValue", "")
            operation_id = webhook_data.get("OperationId", "")
            
            logger.info(f"Processing webhook for order {order_id}, amount: {amount}")
            
            # Verify signature
            if not self._verify_signature(
                self.config.merchant_id,
                amount,
                order_id,
                signature
            ):
                return {
                    "success": False,
                    "order_id": order_id,
                    "status": PaymentStatus.FAILED.value,
                    "amount": amount,
                    "message": "Signature verification failed"
                }
            
            # Verify merchant ID
            if webhook_data.get("MerchantLogin") != self.config.merchant_id:
                logger.warning(f"Merchant ID mismatch in webhook for order {order_id}")
                return {
                    "success": False,
                    "order_id": order_id,
                    "status": PaymentStatus.FAILED.value,
                    "amount": amount,
                    "message": "Merchant ID mismatch"
                }
            
            # Determine payment status
            status = PaymentStatus.SUCCESS
            is_test = webhook_data.get("IsTest") == "1"
            
            logger.info(
                f"Payment webhook processed successfully for order {order_id}, "
                f"operation_id: {operation_id}, test: {is_test}"
            )
            
            return {
                "success": True,
                "order_id": order_id,
                "status": status.value,
                "amount": amount,
                "operation_id": operation_id,
                "is_test": is_test,
                "message": "Payment verified successfully"
            }
            
        except (ValueError, KeyError) as e:
            logger.error(f"Error processing webhook: {str(e)}")
            return {
                "success": False,
                "status": PaymentStatus.FAILED.value,
                "message": f"Error processing webhook: {str(e)}"
            }
    
    def get_payment_status(self, order_id: str) -> Optional[Dict[str, Any]]:
        """
        Get payment status from Robokassa for an order.
        
        Note: This requires additional API credentials and endpoints.
        Basic implementation provided.
        
        Args:
            order_id: Order identifier
            
        Returns:
            Dictionary with payment status or None if failed
        """
        try:
            # This would require additional API credentials
            # Implementation depends on Robokassa API version being used
            logger.info(f"Retrieving payment status for order {order_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error getting payment status: {str(e)}")
            return None
    
    def build_sbp_payment_url(self,
                             amount: float,
                             order_id: str,
                             description: str,
                             phone: str = "") -> str:
        """
        Build SBP-specific payment URL with optimized parameters.
        
        Args:
            amount: Payment amount in rubles
            order_id: Unique order identifier
            description: Payment description
            phone: Customer phone number for SBP
            
        Returns:
            Complete SBP payment URL
        """
        extra_params = {
            "PaymentMethod": "SBP",
        }
        
        if phone:
            extra_params["Phone"] = phone
        
        return self.create_payment_url(
            amount=amount,
            order_id=order_id,
            description=description,
            phone=phone,
            extra_params=extra_params
        )
    
    def validate_webhook_request(self, 
                                webhook_data: Dict[str, Any]) -> tuple[bool, str]:
        """
        Validate webhook request structure and required fields.
        
        Args:
            webhook_data: Webhook data dictionary
            
        Returns:
            Tuple of (is_valid, message)
        """
        required_fields = ["InvId", "Sum", "SignatureValue", "MerchantLogin"]
        
        for field in required_fields:
            if field not in webhook_data:
                return False, f"Missing required field: {field}"
        
        try:
            float(webhook_data["Sum"])
            str(webhook_data["InvId"])
        except (ValueError, TypeError):
            return False, "Invalid Sum or InvId format"
        
        return True, "Valid webhook request"
    
    def close(self):
        """Close the session."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
