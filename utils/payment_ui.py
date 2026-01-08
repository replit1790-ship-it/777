"""
Payment UI Components
Provides reusable UI components for payment and offer functionality.
"""

from dataclasses import dataclass
from typing import Optional, Callable, Dict, Any
from enum import Enum


class ButtonStyle(Enum):
    """Button style variants"""
    PRIMARY = "primary"
    SECONDARY = "secondary"
    SUCCESS = "success"
    DANGER = "danger"
    WARNING = "warning"


class ButtonSize(Enum):
    """Button size variants"""
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"


@dataclass
class OfferButtonConfig:
    """Configuration for offer button"""
    text: str
    style: ButtonStyle = ButtonStyle.PRIMARY
    size: ButtonSize = ButtonSize.MEDIUM
    disabled: bool = False
    icon: Optional[str] = None
    tooltip: Optional[str] = None


class OfferButton:
    """
    Reusable offer button component
    """
    
    def __init__(self, config: OfferButtonConfig, on_click: Optional[Callable] = None):
        """
        Initialize offer button
        
        Args:
            config: Button configuration
            on_click: Callback function when button is clicked
        """
        self.config = config
        self.on_click = on_click
        self._is_loading = False
    
    def render(self) -> Dict[str, Any]:
        """
        Render button as dictionary representation
        
        Returns:
            Dictionary containing button properties
        """
        return {
            "type": "button",
            "text": self.config.text,
            "style": self.config.style.value,
            "size": self.config.size.value,
            "disabled": self.config.disabled or self._is_loading,
            "icon": self.config.icon,
            "tooltip": self.config.tooltip,
            "loading": self._is_loading
        }
    
    def set_loading(self, loading: bool) -> None:
        """Set loading state"""
        self._is_loading = loading
    
    def click(self) -> None:
        """Handle button click"""
        if self.on_click and not self.config.disabled and not self._is_loading:
            self.on_click()


@dataclass
class PaymentOption:
    """Configuration for payment option"""
    id: str
    name: str
    amount: float
    currency: str = "USD"
    description: Optional[str] = None
    features: Optional[list] = None


class PaymentUIComponent:
    """
    Main payment UI component
    Handles displaying payment options and processing
    """
    
    def __init__(self):
        """Initialize payment UI component"""
        self.payment_options: Dict[str, PaymentOption] = {}
        self.selected_option: Optional[str] = None
        self.is_processing = False
    
    def add_payment_option(self, option: PaymentOption) -> None:
        """
        Add a payment option
        
        Args:
            option: Payment option configuration
        """
        self.payment_options[option.id] = option
    
    def remove_payment_option(self, option_id: str) -> None:
        """
        Remove a payment option
        
        Args:
            option_id: ID of option to remove
        """
        if option_id in self.payment_options:
            del self.payment_options[option_id]
    
    def select_option(self, option_id: str) -> bool:
        """
        Select a payment option
        
        Args:
            option_id: ID of option to select
            
        Returns:
            True if option exists and was selected
        """
        if option_id in self.payment_options:
            self.selected_option = option_id
            return True
        return False
    
    def get_selected_option(self) -> Optional[PaymentOption]:
        """
        Get the currently selected payment option
        
        Returns:
            Selected payment option or None
        """
        if self.selected_option:
            return self.payment_options.get(self.selected_option)
        return None
    
    def render_options(self) -> list:
        """
        Render all payment options
        
        Returns:
            List of rendered payment options
        """
        options = []
        for option_id, option in self.payment_options.items():
            options.append({
                "id": option.id,
                "name": option.name,
                "amount": option.amount,
                "currency": option.currency,
                "description": option.description,
                "features": option.features or [],
                "selected": option_id == self.selected_option
            })
        return options
    
    def render(self) -> Dict[str, Any]:
        """
        Render the complete payment UI
        
        Returns:
            Dictionary containing payment UI structure
        """
        return {
            "type": "payment_ui",
            "options": self.render_options(),
            "selected": self.selected_option,
            "processing": self.is_processing
        }


class PaymentProcessor:
    """
    Handles payment processing logic
    """
    
    def __init__(self, api_endpoint: str = ""):
        """
        Initialize payment processor
        
        Args:
            api_endpoint: API endpoint for payment processing
        """
        self.api_endpoint = api_endpoint
        self.transaction_history: list = []
    
    def process_payment(self, payment_option: PaymentOption) -> Dict[str, Any]:
        """
        Process a payment
        
        Args:
            payment_option: Payment option to process
            
        Returns:
            Transaction result
        """
        transaction = {
            "status": "pending",
            "option_id": payment_option.id,
            "amount": payment_option.amount,
            "currency": payment_option.currency
        }
        
        self.transaction_history.append(transaction)
        return transaction
    
    def get_transaction_history(self) -> list:
        """
        Get transaction history
        
        Returns:
            List of transactions
        """
        return self.transaction_history


# Convenience functions for creating common payment options

def create_basic_plan(amount: float = 9.99) -> PaymentOption:
    """Create basic plan payment option"""
    return PaymentOption(
        id="basic",
        name="Basic Plan",
        amount=amount,
        description="Perfect for getting started",
        features=["Feature 1", "Feature 2"]
    )


def create_pro_plan(amount: float = 29.99) -> PaymentOption:
    """Create pro plan payment option"""
    return PaymentOption(
        id="pro",
        name="Pro Plan",
        amount=amount,
        description="For growing teams",
        features=["All Basic features", "Feature 3", "Feature 4", "Priority support"]
    )


def create_enterprise_plan(amount: float = 99.99) -> PaymentOption:
    """Create enterprise plan payment option"""
    return PaymentOption(
        id="enterprise",
        name="Enterprise Plan",
        amount=amount,
        description="Custom solutions for large organizations",
        features=["All Pro features", "Feature 5", "Feature 6", "Dedicated support", "Custom integration"]
    )
