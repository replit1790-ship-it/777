"""
Constants module containing bot commands, messages, emojis, API endpoints,
timeouts, error codes, and payment statuses.
"""

# ============================================================================
# BOT COMMANDS
# ============================================================================

BOT_COMMANDS = {
    "START": "/start",
    "HELP": "/help",
    "BALANCE": "/balance",
    "DEPOSIT": "/deposit",
    "WITHDRAW": "/withdraw",
    "HISTORY": "/history",
    "SETTINGS": "/settings",
    "SUPPORT": "/support",
    "CANCEL": "/cancel",
    "BACK": "/back",
    "STATUS": "/status",
}

# ============================================================================
# MESSAGES
# ============================================================================

MESSAGES = {
    "WELCOME": "Welcome to the Bot! 🎉 Use /help for available commands.",
    "HELP_TEXT": "Available commands:\n/balance - Check your balance\n/deposit - Make a deposit\n/withdraw - Withdraw funds\n/history - View transaction history\n/settings - Manage settings\n/support - Get help",
    "INVALID_COMMAND": "❌ Invalid command. Type /help for available commands.",
    "BALANCE_CHECK": "Your current balance is: {balance}",
    "DEPOSIT_SUCCESS": "✅ Deposit successful! Amount: {amount}",
    "DEPOSIT_FAILED": "❌ Deposit failed. Please try again.",
    "WITHDRAW_SUCCESS": "✅ Withdrawal successful! Amount: {amount}",
    "WITHDRAW_FAILED": "❌ Withdrawal failed. Please try again.",
    "INSUFFICIENT_FUNDS": "❌ Insufficient funds. Your balance: {balance}",
    "TRANSACTION_HISTORY": "📋 Transaction History:\n{history}",
    "NO_TRANSACTIONS": "📭 No transactions found.",
    "SETTINGS_UPDATED": "✅ Settings updated successfully.",
    "SUPPORT_MESSAGE": "📞 Support team has been notified. We'll contact you soon.",
    "OPERATION_CANCELLED": "❌ Operation cancelled.",
    "PROCESSING": "⏳ Processing your request...",
    "ERROR_OCCURRED": "❌ An error occurred. Please try again later.",
    "AUTHENTICATION_FAILED": "🔒 Authentication failed. Please log in again.",
    "SESSION_EXPIRED": "⏰ Your session has expired. Please log in again.",
    "INVALID_INPUT": "⚠️ Invalid input. Please check and try again.",
}

# ============================================================================
# EMOJIS
# ============================================================================

EMOJIS = {
    "SUCCESS": "✅",
    "ERROR": "❌",
    "WARNING": "⚠️",
    "INFO": "ℹ️",
    "LOADING": "⏳",
    "MONEY": "💰",
    "WALLET": "💳",
    "LOCK": "🔒",
    "CLOCK": "⏰",
    "CHART": "📊",
    "HISTORY": "📋",
    "PHONE": "📞",
    "BELL": "🔔",
    "STAR": "⭐",
    "FIRE": "🔥",
    "THUMBS_UP": "👍",
    "THUMBS_DOWN": "👎",
    "ROCKET": "🚀",
    "GEAR": "⚙️",
    "HOUSE": "🏠",
    "USER": "👤",
    "USERS": "👥",
    "EMPTY": "📭",
    "PARTY": "🎉",
}

# ============================================================================
# API ENDPOINTS
# ============================================================================

API_ENDPOINTS = {
    "BASE_URL": "https://api.example.com/v1",
    "AUTH_LOGIN": "/auth/login",
    "AUTH_LOGOUT": "/auth/logout",
    "AUTH_REFRESH": "/auth/refresh",
    "USER_PROFILE": "/user/profile",
    "USER_UPDATE": "/user/update",
    "BALANCE_GET": "/balance/get",
    "BALANCE_UPDATE": "/balance/update",
    "DEPOSIT": "/transactions/deposit",
    "WITHDRAW": "/transactions/withdraw",
    "HISTORY": "/transactions/history",
    "SETTINGS_GET": "/settings/get",
    "SETTINGS_UPDATE": "/settings/update",
    "SUPPORT_CREATE": "/support/create",
    "SUPPORT_LIST": "/support/list",
    "PAYMENT_STATUS": "/payment/status",
    "PAYMENT_VERIFY": "/payment/verify",
}

# ============================================================================
# TIMEOUTS (in seconds)
# ============================================================================

TIMEOUTS = {
    "DEFAULT": 30,
    "SHORT": 5,
    "MEDIUM": 15,
    "LONG": 60,
    "API_REQUEST": 10,
    "DATABASE_QUERY": 20,
    "SESSION": 3600,  # 1 hour
    "TOKEN_EXPIRY": 7200,  # 2 hours
    "CACHE": 300,  # 5 minutes
    "RETRY_DELAY": 2,
    "MAX_RETRY_DELAY": 30,
}

# ============================================================================
# ERROR CODES
# ============================================================================

ERROR_CODES = {
    "SUCCESS": 200,
    "CREATED": 201,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "CONFLICT": 409,
    "RATE_LIMITED": 429,
    "INTERNAL_SERVER_ERROR": 500,
    "SERVICE_UNAVAILABLE": 503,
    "INVALID_INPUT": 1001,
    "AUTHENTICATION_FAILED": 1002,
    "INSUFFICIENT_PERMISSIONS": 1003,
    "RESOURCE_NOT_FOUND": 1004,
    "DATABASE_ERROR": 1005,
    "EXTERNAL_API_ERROR": 1006,
    "TIMEOUT": 1007,
    "DUPLICATE_ENTRY": 1008,
    "OPERATION_FAILED": 1009,
    "INSUFFICIENT_FUNDS": 1010,
    "INVALID_AMOUNT": 1011,
    "TRANSACTION_DECLINED": 1012,
    "UNKNOWN_ERROR": 9999,
}

# ============================================================================
# PAYMENT STATUSES
# ============================================================================

PAYMENT_STATUSES = {
    "PENDING": "pending",
    "PROCESSING": "processing",
    "COMPLETED": "completed",
    "SUCCESSFUL": "successful",
    "FAILED": "failed",
    "CANCELLED": "cancelled",
    "REFUNDED": "refunded",
    "EXPIRED": "expired",
    "ON_HOLD": "on_hold",
    "DISPUTED": "disputed",
    "PARTIALLY_REFUNDED": "partially_refunded",
}

# ============================================================================
# PAYMENT METHODS
# ============================================================================

PAYMENT_METHODS = {
    "CREDIT_CARD": "credit_card",
    "DEBIT_CARD": "debit_card",
    "BANK_TRANSFER": "bank_transfer",
    "E_WALLET": "e_wallet",
    "CRYPTOCURRENCY": "cryptocurrency",
    "PAYPAL": "paypal",
    "STRIPE": "stripe",
    "APPLE_PAY": "apple_pay",
    "GOOGLE_PAY": "google_pay",
}

# ============================================================================
# TRANSACTION TYPES
# ============================================================================

TRANSACTION_TYPES = {
    "DEPOSIT": "deposit",
    "WITHDRAWAL": "withdrawal",
    "TRANSFER": "transfer",
    "REFUND": "refund",
    "CHARGE": "charge",
    "ADJUSTMENT": "adjustment",
}

# ============================================================================
# USER ROLES
# ============================================================================

USER_ROLES = {
    "ADMIN": "admin",
    "MODERATOR": "moderator",
    "USER": "user",
    "GUEST": "guest",
}

# ============================================================================
# CURRENCY
# ============================================================================

CURRENCIES = {
    "USD": "USD",
    "EUR": "EUR",
    "GBP": "GBP",
    "JPY": "JPY",
    "INR": "INR",
    "AUD": "AUD",
    "CAD": "CAD",
}

DEFAULT_CURRENCY = "USD"

# ============================================================================
# PAGINATION
# ============================================================================

PAGINATION = {
    "DEFAULT_PAGE_SIZE": 20,
    "MAX_PAGE_SIZE": 100,
    "MIN_PAGE_SIZE": 1,
}

# ============================================================================
# REGEX PATTERNS
# ============================================================================

REGEX_PATTERNS = {
    "EMAIL": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "PHONE": r"^\+?1?\d{9,15}$",
    "USERNAME": r"^[a-zA-Z0-9_]{3,20}$",
    "PASSWORD": r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$",
    "URL": r"^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$",
}

# ============================================================================
# LIMITS
# ============================================================================

LIMITS = {
    "MAX_DEPOSIT": 100000.00,
    "MIN_DEPOSIT": 0.01,
    "MAX_WITHDRAWAL": 50000.00,
    "MIN_WITHDRAWAL": 0.01,
    "MAX_LOGIN_ATTEMPTS": 5,
    "MAX_API_REQUESTS_PER_MINUTE": 60,
    "MAX_API_REQUESTS_PER_HOUR": 1000,
    "MAX_FILE_SIZE": 10485760,  # 10 MB
    "USERNAME_MAX_LENGTH": 50,
    "PASSWORD_MAX_LENGTH": 128,
}

# ============================================================================
# ENVIRONMENT KEYS
# ============================================================================

ENVIRONMENT_KEYS = {
    "API_KEY": "API_KEY",
    "API_SECRET": "API_SECRET",
    "DATABASE_URL": "DATABASE_URL",
    "SECRET_KEY": "SECRET_KEY",
    "DEBUG": "DEBUG",
    "BOT_TOKEN": "BOT_TOKEN",
    "LOG_LEVEL": "LOG_LEVEL",
}
