# Payment Implementation Guide

## Overview

This document provides comprehensive documentation for the payment system implementation, including Robokassa SBP (Same-Bank Payments) integration, offer buttons, payment handlers, and practical usage examples.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Robokassa SBP Integration](#robokassa-sbp-integration)
3. [Offer Buttons](#offer-buttons)
4. [Payment Handlers](#payment-handlers)
5. [Usage Examples](#usage-examples)
6. [Configuration](#configuration)
7. [Error Handling](#error-handling)
8. [Testing](#testing)
9. [Troubleshooting](#troubleshooting)

---

## Architecture Overview

The payment system is built on a modular architecture consisting of:

- **Payment Provider**: Robokassa SBP as the primary payment gateway
- **Offer System**: Dynamic offer buttons for various payment options
- **Handler Layer**: Business logic for processing payments
- **Integration Points**: WebSocket and HTTP endpoints for real-time updates

### System Flow

```
User → Offer Button → Payment Handler → Robokassa SBP → Payment Processing → Webhook Handler → User Confirmation
```

---

## Robokassa SBP Integration

### What is Robokassa SBP?

Robokassa SBP (Same-Bank Payments) is a Russian payment system that enables instant money transfers between clients of the same bank. It provides:

- Fast payment processing (real-time)
- Lower transaction fees compared to traditional payment methods
- Wide bank support across Russia
- Secure payment infrastructure
- Webhook support for payment confirmation

### Integration Setup

#### 1. Credentials Configuration

Store your Robokassa credentials in environment variables:

```env
ROBOKASSA_LOGIN=your_merchant_login
ROBOKASSA_PASSWORD1=your_password_1
ROBOKASSA_PASSWORD2=your_password_2
ROBOKASSA_TEST_MODE=false
ROBOKASSA_API_KEY=your_api_key
ROBOKASSA_API_URL=https://auth.robokassa.ru/api
```

#### 2. Merchant Account Setup

1. Register at [Robokassa](https://www.robokassa.ru/)
2. Create a merchant account
3. Configure your shop settings:
   - Set up SBP payments method
   - Configure webhook URLs
   - Set success/failure redirect URLs
   - Enable payment notifications

#### 3. Payment URL Generation

```javascript
// Generate a payment URL for Robokassa
function generateRobokassaPaymentUrl(params) {
  const {
    merchantLogin,
    sum,
    invId,
    description,
    email,
    testMode = false
  } = params;

  const baseUrl = testMode 
    ? 'https://test.robokassa.ru/Auth/Login'
    : 'https://auth.robokassa.ru/Auth/Login';

  const url = new URL(baseUrl);
  url.searchParams.append('MerchantLogin', merchantLogin);
  url.searchParams.append('Sum', sum);
  url.searchParams.append('InvId', invId);
  url.searchParams.append('Description', encodeURIComponent(description));
  url.searchParams.append('Email', email);

  return url.toString();
}
```

### Webhook Configuration

#### Receipt of Payment Notification (Result URL)

When a payment is completed, Robokassa sends a webhook to your configured Result URL.

**Request Format:**
```
POST /api/payments/webhook/result
Content-Type: application/x-www-form-urlencoded

MerchantLogin=YourLogin
Sum=100.00
InvId=12345
SignatureValue=MD5_HASH
EMail=customer@example.com
Culture=ru
```

**Signature Verification:**
```javascript
const crypto = require('crypto');

function verifyRobokassaSignature(merchantLogin, sum, invId, password2, signature) {
  const signatureString = `${merchantLogin}:${sum}:${invId}:${password2}`;
  const hash = crypto
    .createHash('md5')
    .update(signatureString)
    .digest('hex')
    .toUpperCase();
  
  return hash === signature.toUpperCase();
}
```

---

## Offer Buttons

### Button Structure

Offer buttons provide users with clear payment options and are the primary interface for initiating payments.

### Types of Offer Buttons

#### 1. Simple Payment Button

```html
<button class="offer-button offer-button--simple" data-amount="100" data-description="Premium Package">
  Pay 100 RUB
</button>
```

```javascript
class SimpleOfferButton {
  constructor(element, options = {}) {
    this.element = element;
    this.amount = parseFloat(element.dataset.amount);
    this.description = element.dataset.description;
    this.options = options;
    this.init();
  }

  init() {
    this.element.addEventListener('click', () => this.handleClick());
  }

  async handleClick() {
    try {
      this.element.disabled = true;
      this.element.textContent = 'Processing...';
      
      const paymentUrl = await this.initiatePayment();
      window.location.href = paymentUrl;
    } catch (error) {
      console.error('Payment initiation failed:', error);
      this.element.disabled = false;
      this.element.textContent = 'Pay ' + this.amount + ' RUB';
      this.showError('Failed to initiate payment. Please try again.');
    }
  }

  async initiatePayment() {
    const response = await fetch('/api/payments/initiate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        amount: this.amount,
        description: this.description,
        returnUrl: window.location.href
      })
    });

    if (!response.ok) {
      throw new Error('Payment initiation failed');
    }

    const data = await response.json();
    return data.paymentUrl;
  }

  showError(message) {
    // Display error to user
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.textContent = message;
    this.element.parentNode.insertBefore(errorDiv, this.element.nextSibling);
    setTimeout(() => errorDiv.remove(), 5000);
  }
}
```

#### 2. Tiered Offer Button

```html
<div class="offer-tiers">
  <button class="offer-button offer-button--tier" data-tier="basic" data-amount="499">
    <span class="tier-name">Basic</span>
    <span class="tier-price">₽499</span>
    <span class="tier-benefits">3 projects</span>
  </button>
  <button class="offer-button offer-button--tier" data-tier="pro" data-amount="999">
    <span class="tier-name">Pro</span>
    <span class="tier-price">₽999</span>
    <span class="tier-benefits">Unlimited projects</span>
  </button>
  <button class="offer-button offer-button--tier" data-tier="enterprise" data-amount="4999">
    <span class="tier-name">Enterprise</span>
    <span class="tier-price">₽4999</span>
    <span class="tier-benefits">Custom features</span>
  </button>
</div>
```

```javascript
class TieredOfferButton {
  constructor(containerElement) {
    this.container = containerElement;
    this.buttons = this.container.querySelectorAll('.offer-button--tier');
    this.init();
  }

  init() {
    this.buttons.forEach(button => {
      button.addEventListener('click', () => this.selectTier(button));
    });
  }

  selectTier(button) {
    // Remove previous selection
    this.buttons.forEach(b => b.classList.remove('active'));
    
    // Add active state
    button.classList.add('active');
    
    // Initiate payment
    this.initiatePayment(button);
  }

  async initiatePayment(button) {
    const tier = button.dataset.tier;
    const amount = parseFloat(button.dataset.amount);

    try {
      const response = await fetch('/api/payments/initiate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount,
          tier,
          description: `${tier.charAt(0).toUpperCase() + tier.slice(1)} Plan`
        })
      });

      const data = await response.json();
      window.location.href = data.paymentUrl;
    } catch (error) {
      console.error('Payment failed:', error);
      this.showError(button, 'Payment failed. Please try again.');
    }
  }

  showError(button, message) {
    const originalText = button.textContent;
    button.textContent = message;
    button.classList.add('error');
    
    setTimeout(() => {
      button.textContent = originalText;
      button.classList.remove('error');
    }, 3000);
  }
}
```

#### 3. Custom Amount Offer Button

```html
<div class="offer-custom-amount">
  <input type="number" id="customAmount" placeholder="Enter amount in RUB" min="100" max="100000" step="100">
  <button class="offer-button offer-button--custom" id="customPayButton">
    Pay Custom Amount
  </button>
</div>
```

```javascript
class CustomAmountOfferButton {
  constructor() {
    this.input = document.getElementById('customAmount');
    this.button = document.getElementById('customPayButton');
    this.init();
  }

  init() {
    this.button.addEventListener('click', () => this.handlePayment());
    this.input.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.handlePayment();
    });
  }

  validateAmount(amount) {
    const numAmount = parseFloat(amount);
    if (isNaN(numAmount)) {
      throw new Error('Please enter a valid amount');
    }
    if (numAmount < 100) {
      throw new Error('Minimum amount is ₽100');
    }
    if (numAmount > 100000) {
      throw new Error('Maximum amount is ₽100,000');
    }
    return numAmount;
  }

  async handlePayment() {
    try {
      const amount = this.validateAmount(this.input.value);
      
      const response = await fetch('/api/payments/initiate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          amount,
          description: `Custom payment - ₽${amount}`
        })
      });

      const data = await response.json();
      window.location.href = data.paymentUrl;
    } catch (error) {
      console.error('Payment error:', error);
      this.showError(error.message);
    }
  }

  showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-notification';
    errorDiv.textContent = message;
    this.input.parentNode.insertBefore(errorDiv, this.input.nextSibling);
    setTimeout(() => errorDiv.remove(), 4000);
  }
}
```

### Button Styling

```css
.offer-button {
  padding: 12px 24px;
  font-size: 16px;
  font-weight: 600;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
}

.offer-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.offer-button:active:not(:disabled) {
  transform: translateY(0);
}

.offer-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.offer-button--tier {
  flex: 1;
  padding: 20px;
  text-align: center;
  margin: 0 10px;
  border: 2px solid transparent;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.offer-button--tier.active {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.1);
  color: #667eea;
}

.offer-button.error {
  background: #f56565;
  box-shadow: 0 4px 15px rgba(245, 101, 101, 0.4);
}

.tier-name {
  font-size: 18px;
  font-weight: 700;
}

.tier-price {
  font-size: 24px;
  font-weight: 800;
  color: #667eea;
}

.tier-benefits {
  font-size: 12px;
  opacity: 0.8;
}
```

---

## Payment Handlers

### Backend Payment Handler

```javascript
// handlers/paymentHandler.js
const crypto = require('crypto');
const axios = require('axios');

class PaymentHandler {
  constructor(config) {
    this.merchantLogin = config.merchantLogin;
    this.password1 = config.password1;
    this.password2 = config.password2;
    this.apiKey = config.apiKey;
    this.apiUrl = config.apiUrl;
    this.testMode = config.testMode || false;
  }

  /**
   * Initiate a payment
   * @param {Object} paymentData - Payment details
   * @returns {Promise<Object>} Payment URL and transaction ID
   */
  async initiatePayment(paymentData) {
    const {
      amount,
      description,
      email,
      userId,
      orderId
    } = paymentData;

    // Validate input
    this.validatePayment(amount, description);

    // Generate unique invoice ID
    const invId = this.generateInvId(userId, orderId);

    // Calculate signature
    const signature = this.calculateSignature(amount, invId, this.password1);

    // Build payment URL
    const paymentUrl = this.buildPaymentUrl({
      merchantLogin: this.merchantLogin,
      sum: amount,
      invId,
      description,
      email,
      signature
    });

    // Store payment record in database
    const paymentRecord = {
      invId,
      userId,
      orderId,
      amount,
      description,
      email,
      status: 'pending',
      createdAt: new Date(),
      expiresAt: new Date(Date.now() + 24 * 60 * 60 * 1000) // 24 hours
    };

    await this.savePaymentRecord(paymentRecord);

    return {
      invId,
      paymentUrl,
      amount,
      expiresAt: paymentRecord.expiresAt
    };
  }

  /**
   * Validate payment parameters
   * @param {number} amount - Payment amount
   * @param {string} description - Payment description
   */
  validatePayment(amount, description) {
    if (!amount || amount < 10) {
      throw new Error('Minimum payment amount is 10 RUB');
    }
    if (amount > 1000000) {
      throw new Error('Maximum payment amount is 1,000,000 RUB');
    }
    if (!description || description.trim().length === 0) {
      throw new Error('Payment description is required');
    }
    if (description.length > 250) {
      throw new Error('Payment description is too long (max 250 characters)');
    }
  }

  /**
   * Generate unique invoice ID
   * @param {string} userId - User ID
   * @param {string} orderId - Order ID
   * @returns {string} Unique invoice ID
   */
  generateInvId(userId, orderId) {
    const timestamp = Date.now();
    const random = Math.random().toString(36).substr(2, 9);
    return `${userId}_${orderId}_${timestamp}_${random}`;
  }

  /**
   * Calculate payment signature
   * @param {number} amount - Payment amount
   * @param {number} invId - Invoice ID
   * @param {string} password - Robokassa password
   * @returns {string} MD5 signature
   */
  calculateSignature(amount, invId, password) {
    const signatureString = `${this.merchantLogin}:${amount}:${invId}:${password}`;
    return crypto
      .createHash('md5')
      .update(signatureString)
      .digest('hex')
      .toUpperCase();
  }

  /**
   * Build payment URL
   * @param {Object} params - Payment parameters
   * @returns {string} Complete payment URL
   */
  buildPaymentUrl(params) {
    const {
      merchantLogin,
      sum,
      invId,
      description,
      email,
      signature
    } = params;

    const baseUrl = this.testMode
      ? 'https://test.robokassa.ru/Auth/Login'
      : 'https://auth.robokassa.ru/Auth/Login';

    const url = new URL(baseUrl);
    url.searchParams.append('MerchantLogin', merchantLogin);
    url.searchParams.append('Sum', sum);
    url.searchParams.append('InvId', invId);
    url.searchParams.append('Description', encodeURIComponent(description));
    url.searchParams.append('SignatureValue', signature);
    url.searchParams.append('Email', email);
    url.searchParams.append('Culture', 'ru');

    return url.toString();
  }

  /**
   * Handle payment confirmation webhook
   * @param {Object} webhookData - Webhook payload from Robokassa
   * @returns {Promise<Object>} Confirmation result
   */
  async handlePaymentConfirmation(webhookData) {
    const {
      MerchantLogin,
      Sum,
      InvId,
      SignatureValue,
      EMail,
      Status
    } = webhookData;

    // Verify signature
    if (!this.verifySignature(MerchantLogin, Sum, InvId, SignatureValue)) {
      throw new Error('Invalid signature');
    }

    // Retrieve payment record
    const paymentRecord = await this.getPaymentRecord(InvId);
    if (!paymentRecord) {
      throw new Error('Payment record not found');
    }

    // Verify amount
    if (parseFloat(paymentRecord.amount) !== parseFloat(Sum)) {
      throw new Error('Amount mismatch');
    }

    // Update payment status
    const updatedRecord = await this.updatePaymentStatus(InvId, 'confirmed');

    // Trigger user-specific actions
    await this.processPaymentConfirmation(updatedRecord);

    return {
      success: true,
      invId: InvId,
      message: 'Payment confirmed'
    };
  }

  /**
   * Verify webhook signature
   * @param {string} merchantLogin - Merchant login
   * @param {number} sum - Payment amount
   * @param {number} invId - Invoice ID
   * @param {string} signature - Provided signature
   * @returns {boolean} Signature validity
   */
  verifySignature(merchantLogin, sum, invId, signature) {
    const expectedSignature = this.calculateSignature(sum, invId, this.password2);
    return expectedSignature === signature.toUpperCase();
  }

  /**
   * Get payment record
   * @param {string} invId - Invoice ID
   * @returns {Promise<Object>} Payment record
   */
  async getPaymentRecord(invId) {
    // Implementation depends on your database
    // This is a placeholder
    return await db.payments.findOne({ invId });
  }

  /**
   * Save payment record
   * @param {Object} record - Payment record
   * @returns {Promise<void>}
   */
  async savePaymentRecord(record) {
    // Implementation depends on your database
    return await db.payments.insertOne(record);
  }

  /**
   * Update payment status
   * @param {string} invId - Invoice ID
   * @param {string} status - New status
   * @returns {Promise<Object>} Updated record
   */
  async updatePaymentStatus(invId, status) {
    return await db.payments.findOneAndUpdate(
      { invId },
      { 
        $set: { 
          status,
          updatedAt: new Date()
        } 
      },
      { returnDocument: 'after' }
    );
  }

  /**
   * Process payment confirmation
   * @param {Object} paymentRecord - Payment record
   * @returns {Promise<void>}
   */
  async processPaymentConfirmation(paymentRecord) {
    const { userId, orderId, amount } = paymentRecord;

    // Update user account balance or subscription
    await db.users.findByIdAndUpdate(userId, {
      $inc: { balance: amount },
      $set: { lastPaymentDate: new Date() }
    });

    // Update order status
    await db.orders.findByIdAndUpdate(orderId, {
      $set: { 
        status: 'paid',
        paidAt: new Date(),
        paidAmount: amount
      }
    });

    // Emit event for other systems
    this.emitPaymentConfirmed(userId, orderId, amount);
  }

  /**
   * Emit payment confirmed event
   * @param {string} userId - User ID
   * @param {string} orderId - Order ID
   * @param {number} amount - Payment amount
   */
  emitPaymentConfirmed(userId, orderId, amount) {
    // This could trigger notifications, emails, webhooks, etc.
    console.log(`Payment confirmed: User ${userId}, Order ${orderId}, Amount ₽${amount}`);
    // Example: emit to WebSocket, send email, trigger business logic
  }
}

module.exports = PaymentHandler;
```

### Express Route Handler

```javascript
// routes/payments.js
const express = require('express');
const router = express.Router();
const PaymentHandler = require('../handlers/paymentHandler');

const paymentHandler = new PaymentHandler({
  merchantLogin: process.env.ROBOKASSA_LOGIN,
  password1: process.env.ROBOKASSA_PASSWORD1,
  password2: process.env.ROBOKASSA_PASSWORD2,
  apiKey: process.env.ROBOKASSA_API_KEY,
  apiUrl: process.env.ROBOKASSA_API_URL,
  testMode: process.env.ROBOKASSA_TEST_MODE === 'true'
});

/**
 * POST /api/payments/initiate
 * Initiate a payment
 */
router.post('/initiate', async (req, res) => {
  try {
    const { amount, description, email, userId, orderId } = req.body;

    // Validate request
    if (!amount || !description || !email) {
      return res.status(400).json({
        error: 'Missing required parameters: amount, description, email'
      });
    }

    // Get or use session user ID
    const effectiveUserId = userId || req.session?.userId;
    if (!effectiveUserId) {
      return res.status(401).json({ error: 'User not authenticated' });
    }

    // Initiate payment
    const paymentResult = await paymentHandler.initiatePayment({
      amount: parseFloat(amount),
      description,
      email,
      userId: effectiveUserId,
      orderId: orderId || `order_${Date.now()}`
    });

    res.json({
      success: true,
      ...paymentResult
    });
  } catch (error) {
    console.error('Payment initiation error:', error);
    res.status(400).json({
      error: error.message || 'Payment initiation failed'
    });
  }
});

/**
 * POST /api/payments/webhook/result
 * Robokassa Result URL webhook
 */
router.post('/webhook/result', async (req, res) => {
  try {
    const confirmationResult = await paymentHandler.handlePaymentConfirmation(req.body);

    // Return OK response to Robokassa
    res.status(200).send('OK');
  } catch (error) {
    console.error('Webhook processing error:', error);
    res.status(400).send('ERROR');
  }
});

/**
 * POST /api/payments/webhook/success
 * Robokassa Success URL webhook (optional)
 */
router.post('/webhook/success', async (req, res) => {
  try {
    const { InvId } = req.body;
    
    // Log success
    console.log(`Payment success: Invoice ${InvId}`);
    
    res.json({ success: true });
  } catch (error) {
    console.error('Success webhook error:', error);
    res.status(400).json({ error: 'Error processing success notification' });
  }
});

/**
 * GET /api/payments/status/:invId
 * Check payment status
 */
router.get('/status/:invId', async (req, res) => {
  try {
    const { invId } = req.params;

    const paymentRecord = await paymentHandler.getPaymentRecord(invId);
    if (!paymentRecord) {
      return res.status(404).json({ error: 'Payment not found' });
    }

    res.json({
      invId: paymentRecord.invId,
      status: paymentRecord.status,
      amount: paymentRecord.amount,
      createdAt: paymentRecord.createdAt,
      updatedAt: paymentRecord.updatedAt
    });
  } catch (error) {
    console.error('Status check error:', error);
    res.status(500).json({ error: 'Failed to check payment status' });
  }
});

module.exports = router;
```

---

## Usage Examples

### Example 1: Basic E-Commerce Integration

```html
<!DOCTYPE html>
<html>
<head>
  <title>Buy Premium Features</title>
  <style>
    body {
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto;
      max-width: 1000px;
      margin: 0 auto;
      padding: 20px;
      background: #f5f5f5;
    }
    
    .pricing-container {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
      gap: 20px;
      margin-top: 40px;
    }

    .pricing-card {
      background: white;
      border-radius: 12px;
      padding: 30px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      text-align: center;
    }

    .pricing-card h3 {
      margin: 0 0 10px 0;
      color: #333;
    }

    .price {
      font-size: 48px;
      font-weight: bold;
      color: #667eea;
      margin: 20px 0;
    }

    .features {
      text-align: left;
      margin: 20px 0;
      color: #666;
    }

    .features li {
      padding: 8px 0;
      border-bottom: 1px solid #eee;
    }
  </style>
</head>
<body>
  <h1>Choose Your Plan</h1>
  
  <div class="pricing-container">
    <div class="pricing-card">
      <h3>Starter</h3>
      <div class="price">₽299</div>
      <ul class="features">
        <li>✓ 5 Projects</li>
        <li>✓ Basic Support</li>
        <li>✓ 10 GB Storage</li>
      </ul>
      <button class="offer-button" data-amount="299" data-description="Starter Plan">
        Get Started
      </button>
    </div>

    <div class="pricing-card">
      <h3>Professional</h3>
      <div class="price">₽799</div>
      <ul class="features">
        <li>✓ Unlimited Projects</li>
        <li>✓ Priority Support</li>
        <li>✓ 100 GB Storage</li>
        <li>✓ Advanced Analytics</li>
      </ul>
      <button class="offer-button" data-amount="799" data-description="Professional Plan">
        Upgrade Now
      </button>
    </div>

    <div class="pricing-card">
      <h3>Enterprise</h3>
      <div class="price">₽2999</div>
      <ul class="features">
        <li>✓ Custom Projects</li>
        <li>✓ Dedicated Support</li>
        <li>✓ Unlimited Storage</li>
        <li>✓ Custom Integrations</li>
      </ul>
      <button class="offer-button" data-amount="2999" data-description="Enterprise Plan">
        Contact Sales
      </button>
    </div>
  </div>

  <script src="/js/offer-buttons.js"></script>
  <script>
    // Initialize all offer buttons
    document.querySelectorAll('.offer-button').forEach(button => {
      new SimpleOfferButton(button);
    });
  </script>
</body>
</html>
```

### Example 2: Payment Status Monitoring

```javascript
// Client-side payment status polling
class PaymentStatusMonitor {
  constructor(invId, options = {}) {
    this.invId = invId;
    this.pollInterval = options.pollInterval || 3000; // 3 seconds
    this.maxPolls = options.maxPolls || 120; // 6 minutes total
    this.polls = 0;
    this.isComplete = false;
  }

  async startMonitoring() {
    console.log(`Starting payment status monitoring for ${this.invId}`);
    
    while (this.polls < this.maxPolls && !this.isComplete) {
      try {
        const status = await this.checkStatus();
        
        if (status.status === 'confirmed') {
          this.handlePaymentSuccess(status);
          this.isComplete = true;
          break;
        }
        
        this.polls++;
        await this.sleep(this.pollInterval);
      } catch (error) {
        console.error('Error checking payment status:', error);
        this.polls++;
        await this.sleep(this.pollInterval);
      }
    }

    if (!this.isComplete) {
      this.handlePaymentTimeout();
    }
  }

  async checkStatus() {
    const response = await fetch(`/api/payments/status/${this.invId}`);
    if (!response.ok) {
      throw new Error('Failed to check status');
    }
    return response.json();
  }

  handlePaymentSuccess(status) {
    console.log('Payment confirmed!', status);
    // Update UI, redirect, etc.
    window.location.href = '/success?invId=' + this.invId;
  }

  handlePaymentTimeout() {
    console.warn('Payment confirmation timeout');
    // Show timeout message, offer retry
  }

  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Usage
const monitor = new PaymentStatusMonitor('user123_order456_1234567890_abc123def');
monitor.startMonitoring();
```

### Example 3: Order Fulfillment After Payment

```javascript
// Backend order fulfillment
class OrderFulfillmentService {
  async onPaymentConfirmed(paymentRecord) {
    const { userId, orderId, amount } = paymentRecord;

    try {
      // 1. Verify payment
      await this.verifyPayment(paymentRecord);

      // 2. Update inventory
      const order = await this.getOrder(orderId);
      await this.reduceInventory(order.items);

      // 3. Generate digital products
      const downloads = await this.generateDigitalAssets(order);

      // 4. Update user account
      await this.updateUserProfile(userId, {
        isPremium: true,
        premiumExpires: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000)
      });

      // 5. Send confirmation email
      await this.sendConfirmationEmail(userId, {
        orderId,
        amount,
        downloads,
        receipt: await this.generateReceipt(paymentRecord)
      });

      // 6. Log activity
      await this.logActivity({
        userId,
        type: 'payment_confirmed',
        orderId,
        amount,
        timestamp: new Date()
      });

      return { success: true, orderId };
    } catch (error) {
      console.error('Fulfillment error:', error);
      // Handle error - may need manual intervention
      await this.notifyAdmins('Payment fulfillment failed', { paymentRecord, error });
      throw error;
    }
  }

  async verifyPayment(record) {
    // Verify payment details
    if (!record.invId || record.status !== 'confirmed') {
      throw new Error('Invalid payment');
    }
  }

  async getOrder(orderId) {
    return await db.orders.findById(orderId);
  }

  async reduceInventory(items) {
    for (const item of items) {
      await db.inventory.findByIdAndUpdate(item.id, {
        $inc: { quantity: -item.quantity }
      });
    }
  }

  async generateDigitalAssets(order) {
    // Generate download links, licenses, etc.
    return [];
  }

  async updateUserProfile(userId, updates) {
    return await db.users.findByIdAndUpdate(userId, { $set: updates });
  }

  async sendConfirmationEmail(userId, data) {
    const user = await db.users.findById(userId);
    // Send email via email service
  }

  async generateReceipt(paymentRecord) {
    // Generate receipt PDF or HTML
    return { receiptUrl: `/receipts/${paymentRecord.invId}` };
  }

  async logActivity(activity) {
    return await db.activityLog.insertOne(activity);
  }

  async notifyAdmins(message, data) {
    // Send admin notification
    console.error(message, data);
  }
}
```

---

## Configuration

### Environment Variables

```env
# Robokassa Configuration
ROBOKASSA_LOGIN=your_merchant_login
ROBOKASSA_PASSWORD1=your_password_1
ROBOKASSA_PASSWORD2=your_password_2
ROBOKASSA_TEST_MODE=false
ROBOKASSA_API_KEY=your_api_key
ROBOKASSA_API_URL=https://auth.robokassa.ru/api

# Payment System
PAYMENT_MIN_AMOUNT=10
PAYMENT_MAX_AMOUNT=1000000
PAYMENT_CURRENCY=RUB
PAYMENT_WEBHOOK_SECRET=your_webhook_secret

# URLs
PAYMENT_SUCCESS_URL=https://example.com/payment-success
PAYMENT_FAILURE_URL=https://example.com/payment-failure
PAYMENT_WEBHOOK_URL=https://example.com/api/payments/webhook/result

# Database
MONGODB_URI=mongodb://localhost:27017/payments_db
```

### Configuration File

```javascript
// config/payment.config.js
module.exports = {
  robokassa: {
    merchantLogin: process.env.ROBOKASSA_LOGIN,
    password1: process.env.ROBOKASSA_PASSWORD1,
    password2: process.env.ROBOKASSA_PASSWORD2,
    apiKey: process.env.ROBOKASSA_API_KEY,
    apiUrl: process.env.ROBOKASSA_API_URL,
    testMode: process.env.ROBOKASSA_TEST_MODE === 'true'
  },

  payment: {
    minAmount: parseInt(process.env.PAYMENT_MIN_AMOUNT || '10'),
    maxAmount: parseInt(process.env.PAYMENT_MAX_AMOUNT || '1000000'),
    currency: process.env.PAYMENT_CURRENCY || 'RUB',
    webhookSecret: process.env.PAYMENT_WEBHOOK_SECRET
  },

  urls: {
    success: process.env.PAYMENT_SUCCESS_URL,
    failure: process.env.PAYMENT_FAILURE_URL,
    webhook: process.env.PAYMENT_WEBHOOK_URL
  },

  database: {
    uri: process.env.MONGODB_URI,
    options: {
      useNewUrlParser: true,
      useUnifiedTopology: true
    }
  }
};
```

---

## Error Handling

### Common Error Scenarios

#### 1. Invalid Amount

```javascript
try {
  await paymentHandler.initiatePayment({ amount: 5 }); // Less than minimum
} catch (error) {
  console.error(error.message);
  // Output: "Minimum payment amount is 10 RUB"
}
```

#### 2. Signature Verification Failed

```javascript
// Invalid webhook signature
const isValid = paymentHandler.verifySignature(
  'wrong_merchant',
  '100',
  '12345',
  'invalid_signature'
);
// Returns: false - Reject the webhook
```

#### 3. Duplicate Payment

```javascript
// Prevent duplicate payments
const existingPayment = await db.payments.findOne({
  invId: duplicateInvId,
  status: 'confirmed'
});

if (existingPayment) {
  throw new Error('Payment already confirmed');
}
```

### Error Response Format

```javascript
// Standard error responses
{
  "error": "Payment description is required",
  "code": "INVALID_DESCRIPTION",
  "details": {
    "field": "description",
    "reason": "empty_string"
  }
}
```

### Error Logging

```javascript
class ErrorLogger {
  static logPaymentError(error, context) {
    const errorRecord = {
      timestamp: new Date(),
      message: error.message,
      stack: error.stack,
      context,
      severity: 'high'
    };

    db.errorLogs.insertOne(errorRecord);
    console.error('[PAYMENT ERROR]', errorRecord);
  }
}
```

---

## Testing

### Unit Tests for Payment Handler

```javascript
// test/paymentHandler.test.js
const PaymentHandler = require('../handlers/paymentHandler');

describe('PaymentHandler', () => {
  let handler;

  beforeEach(() => {
    handler = new PaymentHandler({
      merchantLogin: 'test_merchant',
      password1: 'test_password_1',
      password2: 'test_password_2',
      testMode: true
    });
  });

  describe('validatePayment', () => {
    it('should reject amount less than minimum', () => {
      expect(() => {
        handler.validatePayment(5, 'Test payment');
      }).toThrow('Minimum payment amount is 10 RUB');
    });

    it('should reject amount greater than maximum', () => {
      expect(() => {
        handler.validatePayment(2000000, 'Test payment');
      }).toThrow('Maximum payment amount is 1,000,000 RUB');
    });

    it('should reject empty description', () => {
      expect(() => {
        handler.validatePayment(100, '');
      }).toThrow('Payment description is required');
    });

    it('should accept valid payment', () => {
      expect(() => {
        handler.validatePayment(100, 'Valid payment');
      }).not.toThrow();
    });
  });

  describe('calculateSignature', () => {
    it('should calculate correct MD5 signature', () => {
      const signature = handler.calculateSignature(100, 12345, 'password');
      expect(signature).toBe('expectedHash');
    });
  });

  describe('verifySignature', () => {
    it('should verify correct signature', () => {
      const isValid = handler.verifySignature('merchant', '100', '12345', 'signature');
      expect(isValid).toBe(true);
    });

    it('should reject incorrect signature', () => {
      const isValid = handler.verifySignature('merchant', '100', '12345', 'wrong');
      expect(isValid).toBe(false);
    });
  });
});
```

### Integration Tests

```javascript
// test/payment.integration.test.js
describe('Payment API Integration', () => {
  let app;
  let request;

  beforeEach(() => {
    app = require('../app');
    request = require('supertest')(app);
  });

  describe('POST /api/payments/initiate', () => {
    it('should initiate payment successfully', async () => {
      const response = await request
        .post('/api/payments/initiate')
        .send({
          amount: 100,
          description: 'Test payment',
          email: 'test@example.com'
        });

      expect(response.status).toBe(200);
      expect(response.body).toHaveProperty('paymentUrl');
      expect(response.body).toHaveProperty('invId');
    });

    it('should reject invalid amount', async () => {
      const response = await request
        .post('/api/payments/initiate')
        .send({
          amount: 5,
          description: 'Test payment',
          email: 'test@example.com'
        });

      expect(response.status).toBe(400);
      expect(response.body.error).toContain('Minimum');
    });
  });

  describe('POST /api/payments/webhook/result', () => {
    it('should process valid webhook', async () => {
      const response = await request
        .post('/api/payments/webhook/result')
        .send({
          MerchantLogin: 'test_merchant',
          Sum: '100',
          InvId: 'test_inv_123',
          SignatureValue: 'validSignature',
          EMail: 'test@example.com'
        });

      expect(response.status).toBe(200);
    });
  });
});
```

---

## Troubleshooting

### Issue: Payment URL not loading

**Possible Causes:**
- Invalid merchant login
- Test mode enabled for production URLs
- Incorrect signature calculation

**Solution:**
```javascript
// Verify merchant login and environment
console.log('Merchant Login:', process.env.ROBOKASSA_LOGIN);
console.log('Test Mode:', process.env.ROBOKASSA_TEST_MODE);
console.log('Payment URL:', paymentUrl);
```

### Issue: Webhook not being received

**Possible Causes:**
- Webhook URL not configured in Robokassa settings
- Server not accessible from internet
- SSL certificate issues

**Solution:**
```javascript
// Log all incoming webhooks
router.post('/webhook/result', (req, res, next) => {
  console.log('Webhook received:', {
    timestamp: new Date().toISOString(),
    body: req.body,
    headers: req.headers,
    ip: req.ip
  });
  
  next();
});
```

### Issue: Signature verification fails

**Possible Causes:**
- Using wrong password (should use password2 for verification)
- Incorrect field order in signature string
- Case sensitivity issues

**Solution:**
```javascript
// Debug signature verification
function debugSignature(merchantLogin, sum, invId, signature, password2) {
  const signatureString = `${merchantLogin}:${sum}:${invId}:${password2}`;
  const hash = crypto
    .createHash('md5')
    .update(signatureString)
    .digest('hex')
    .toUpperCase();

  console.log('Expected signature:', hash);
  console.log('Provided signature:', signature.toUpperCase());
  console.log('Match:', hash === signature.toUpperCase());
  
  return hash === signature.toUpperCase();
}
```

### Issue: Duplicate payment confirmations

**Possible Causes:**
- Webhook retries from Robokassa
- Multiple webhook handlers processing same payment

**Solution:**
```javascript
// Idempotent payment processing
async function handlePaymentConfirmation(webhookData) {
  const { InvId } = webhookData;

  // Check if already processed
  const existingRecord = await db.payments.findOne({
    invId: InvId,
    status: 'confirmed'
  });

  if (existingRecord) {
    console.log('Payment already confirmed, skipping');
    return existingRecord;
  }

  // Process payment
  return await processNewPayment(webhookData);
}
```

### Issue: Payment amount mismatch

**Possible Causes:**
- Rounding errors in decimal calculations
- Currency conversion issues
- Database storage precision

**Solution:**
```javascript
// Use fixed-point arithmetic for amounts
const Decimal = require('decimal.js');

function verifyAmount(recordAmount, webhookAmount) {
  const record = new Decimal(recordAmount);
  const webhook = new Decimal(webhookAmount);
  
  return record.equals(webhook);
}
```

---

## Additional Resources

- [Robokassa Official Documentation](https://robokassa.ru/)
- [Robokassa API Reference](https://robokassa.ru/Doc/Api)
- [Payment Best Practices](https://robokassa.ru/en/Doc/Ru)
- [Security Guidelines](https://robokassa.ru/en/Doc/RuMerchantInterface)

---

## Support

For issues or questions about the payment implementation:

1. Check the **Troubleshooting** section above
2. Review Robokassa documentation
3. Check payment logs: `tail -f logs/payment.log`
4. Verify webhook configuration in Robokassa dashboard
5. Contact Robokassa support: support@robokassa.ru

---

**Document Version:** 1.0  
**Last Updated:** 2026-01-08  
**Maintainer:** replit1790-ship-it
