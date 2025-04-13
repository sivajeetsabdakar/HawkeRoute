# HawkeRoute API Reference

This document provides a comprehensive reference for all API endpoints available in the HawkeRoute backend. Frontend developers can use this as a guide to understand the API structure, request/response formats, and authentication requirements.

## Table of Contents

- [Authentication](#authentication)
  - [Register](#register)
  - [Login](#login)
  - [Refresh Token](#refresh-token)
  - [Get Current User](#get-current-user)
  - [Logout](#logout)
  - [Password Reset Request](#password-reset-request)
  - [Password Reset](#password-reset)
  - [Verify Email](#verify-email)
  - [Resend Verification](#resend-verification)
- [User Management](#user-management)
- [Hawker Management](#hawker-management)
- [Products](#products)
- [Orders](#orders)
- [Deliveries](#deliveries)
- [Payments](#payments)
- [Location](#location)

## Authentication

All authenticated endpoints require a valid JWT token sent in the Authorization header:

```
Authorization: Bearer <access_token>
```

### Register

Register a new user (customer or hawker).

- **URL**: `/api/auth/register`
- **Method**: `POST`
- **Auth required**: No

**Request Body**:

```json
{
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "12345678",
  "password": "securepassword",
  "role": "customer",
  // For hawkers only
  "business_name": "John's Food",
  "business_address": "123 Main St",
  "latitude": 1.2345,
  "longitude": 103.8765
}
```

**Success Response**:

```json
{
  "message": "Registration successful",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "12345678",
    "role": "customer",
    // Additional fields for hawkers
    "business_name": "John's Food",
    "business_address": "123 Main St",
    "latitude": 1.2345,
    "longitude": 103.8765,
    "created_at": "2023-07-15T10:30:45"
  },
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG..."
}
```

**Error Responses**:

- 400 Bad Request - Missing required fields
- 409 Conflict - Email or phone already registered

### Login

Authenticate a user.

- **URL**: `/api/auth/login`
- **Method**: `POST`
- **Auth required**: No

**Request Body**:

```json
{
  "email": "john@example.com",
  "password": "securepassword"
}
```

**Success Response**:

```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "12345678",
    "role": "customer",
    // Additional fields based on role
    "created_at": "2023-07-15T10:30:45"
  },
  "access_token": "eyJhbG...",
  "refresh_token": "eyJhbG..."
}
```

**Error Responses**:

- 400 Bad Request - Missing email or password
- 401 Unauthorized - Invalid email or password
- 403 Forbidden - Account is deactivated

### Refresh Token

Get a new access token using a refresh token.

- **URL**: `/api/auth/refresh`
- **Method**: `POST`
- **Auth required**: Yes (Refresh token)

**Success Response**:

```json
{
  "access_token": "eyJhbG..."
}
```

### Get Current User

Get the currently logged-in user's details.

- **URL**: `/api/auth/me`
- **Method**: `GET`
- **Auth required**: Yes

**Success Response**:

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "12345678",
  "role": "customer",
  // Additional fields based on role
  "created_at": "2023-07-15T10:30:45"
}
```

### Logout

Invalidate the current access token.

- **URL**: `/api/auth/logout`
- **Method**: `POST`
- **Auth required**: Yes

**Success Response**:

```json
{
  "message": "Successfully logged out"
}
```

### Password Reset Request

Request a password reset link.

- **URL**: `/api/auth/password-reset-request`
- **Method**: `POST`
- **Auth required**: No

**Request Body**:

```json
{
  "email": "john@example.com"
}
```

**Success Response**:

```json
{
  "message": "If your email is registered, you will receive a password reset link"
}
```

### Password Reset

Reset password using a valid reset token.

- **URL**: `/api/auth/password-reset`
- **Method**: `POST`
- **Auth required**: Yes (Password reset token)

**Request Body**:

```json
{
  "new_password": "newSecurePassword"
}
```

**Success Response**:

```json
{
  "message": "Password successfully reset"
}
```

### Verify Email

Verify email address using verification token.

- **URL**: `/api/auth/verify-email`
- **Method**: `POST`
- **Auth required**: Yes (Email verification token)

**Success Response**:

```json
{
  "message": "Email successfully verified"
}
```

### Resend Verification

Resend email verification link.

- **URL**: `/api/auth/resend-verification`
- **Method**: `POST`
- **Auth required**: Yes

**Success Response**:

```json
{
  "message": "Verification email sent"
}
```

## User Management

### Get User Profile

Get the current user's profile.

- **URL**: `/api/user/profile`
- **Method**: `GET`
- **Auth required**: Yes

**Success Response**:

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "12345678",
  "role": "customer",
  "created_at": "2023-07-15T10:30:45",
  "updated_at": "2023-07-15T14:20:15"
}
```

### Update User Profile

Update the current user's profile.

- **URL**: `/api/user/profile`
- **Method**: `PUT`
- **Auth required**: Yes

**Request Body**:

```json
{
  "name": "John Smith",
  "phone": "87654321"
}
```

**Success Response**:

```json
{
  "id": 1,
  "name": "John Smith",
  "email": "john@example.com",
  "phone": "87654321",
  "role": "customer",
  "created_at": "2023-07-15T10:30:45",
  "updated_at": "2023-07-16T09:15:30"
}
```

## Hawker Management

### Get Hawker Orders

Get orders assigned to the hawker.

- **URL**: `/api/hawker/orders`
- **Method**: `GET`
- **Auth required**: Yes (Hawker role)
- **Query Parameters**:
  - `page` (optional): Page number (default: 1)
  - `per_page` (optional): Items per page (default: 10)
  - `status` (optional): Filter by order status

**Success Response**:

```json
{
  "items": [
    {
      "id": 1,
      "customer_id": 2,
      "customer_name": "Jane Doe",
      "status": "pending",
      "total_amount": 25.5,
      "delivery_address": "456 Main St",
      "delivery_latitude": 1.3421,
      "delivery_longitude": 103.8765,
      "created_at": "2023-07-15T12:30:45",
      "items": [
        {
          "product_id": 1,
          "product_name": "Chicken Rice",
          "quantity": 2,
          "price": 5.5
        },
        {
          "product_id": 3,
          "product_name": "Mee Goreng",
          "quantity": 1,
          "price": 4.5
        }
      ]
    }
  ],
  "total": 5,
  "page": 1,
  "per_page": 10,
  "pages": 1
}
```

### Get Hawker Business Profile

Get the hawker's business profile.

- **URL**: `/api/hawker/profile`
- **Method**: `GET`
- **Auth required**: Yes (Hawker role)

**Success Response**:

```json
{
  "id": 1,
  "name": "John Doe",
  "email": "john@example.com",
  "phone": "12345678",
  "business_name": "John's Food",
  "business_address": "123 Main St",
  "latitude": 1.2345,
  "longitude": 103.8765,
  "is_active": true,
  "created_at": "2023-07-15T10:30:45",
  "updated_at": "2023-07-15T14:20:15"
}
```

### Update Hawker Business Profile

Update the hawker's business profile.

- **URL**: `/api/hawker/profile`
- **Method**: `PUT`
- **Auth required**: Yes (Hawker role)

**Request Body**:

```json
{
  "name": "John Smith",
  "phone": "87654321",
  "business_name": "John's Delicious Food",
  "business_address": "456 Main St",
  "latitude": 1.3456,
  "longitude": 103.9876
}
```

**Success Response**:

```json
{
  "id": 1,
  "name": "John Smith",
  "email": "john@example.com",
  "phone": "87654321",
  "business_name": "John's Delicious Food",
  "business_address": "456 Main St",
  "latitude": 1.3456,
  "longitude": 103.9876,
  "is_active": true,
  "created_at": "2023-07-15T10:30:45",
  "updated_at": "2023-07-16T09:15:30"
}
```

### Get Optimized Route

Get optimized delivery route for the hawker.

- **URL**: `/api/hawker/route`
- **Method**: `GET`
- **Auth required**: Yes (Hawker role)
- **Query Parameters**:
  - `date` (optional): Delivery date (format: YYYY-MM-DD)

**Success Response**:

```json
{
  "success": true,
  "message": "Route optimized successfully",
  "route_id": 123,
  "total_distance": 15000,
  "estimated_duration": 3600,
  "stops": [
    {
      "order_id": 1,
      "address": "456 Main St",
      "customer_name": "Jane Doe",
      "items": [
        {
          "product_id": 1,
          "product_name": "Chicken Rice",
          "quantity": 2
        },
        {
          "product_id": 3,
          "product_name": "Mee Goreng",
          "quantity": 1
        }
      ]
    },
    {
      "order_id": 2,
      "address": "789 Orchard Rd",
      "customer_name": "Bob Smith",
      "items": [
        {
          "product_id": 2,
          "product_name": "Nasi Lemak",
          "quantity": 3
        }
      ]
    }
  ]
}
```

### Update Hawker Location

Update hawker's current location.

- **URL**: `/api/hawker/location`
- **Method**: `PUT`
- **Auth required**: Yes (Hawker role)

**Request Body**:

```json
{
  "latitude": 1.3456,
  "longitude": 103.9876
}
```

**Success Response**:

```json
{
  "message": "Location updated successfully"
}
```

## Products

### List Products

Get a list of all products or filter by hawker.

- **URL**: `/api/products`
- **Method**: `GET`
- **Auth required**: No
- **Query Parameters**:
  - `hawker_id` (optional): Filter products by hawker ID
  - `is_available` (optional): Filter by availability (true/false)

**Success Response**:

```json
[
  {
    "id": 1,
    "hawker_id": 3,
    "name": "Chicken Rice",
    "description": "Delicious Singaporean chicken rice",
    "price": 5.5,
    "image_url": "https://example.com/images/chicken-rice.jpg",
    "is_available": true,
    "created_at": "2023-07-10T08:30:45",
    "updated_at": "2023-07-10T08:30:45"
  },
  {
    "id": 2,
    "hawker_id": 3,
    "name": "Nasi Lemak",
    "description": "Fragrant coconut rice with sides",
    "price": 6.5,
    "image_url": "https://example.com/images/nasi-lemak.jpg",
    "is_available": true,
    "created_at": "2023-07-10T08:35:20",
    "updated_at": "2023-07-10T08:35:20"
  }
]
```

### Create Product

Create a new product (Hawkers only).

- **URL**: `/api/products`
- **Method**: `POST`
- **Auth required**: Yes (Hawker role)

**Request Body**:

```json
{
  "name": "Mee Goreng",
  "description": "Spicy fried noodles",
  "price": 4.5,
  "image_url": "https://example.com/images/mee-goreng.jpg",
  "is_available": true
}
```

**Success Response**:

```json
{
  "id": 3,
  "hawker_id": 3,
  "name": "Mee Goreng",
  "description": "Spicy fried noodles",
  "price": 4.5,
  "image_url": "https://example.com/images/mee-goreng.jpg",
  "is_available": true,
  "created_at": "2023-07-15T14:20:30",
  "updated_at": "2023-07-15T14:20:30"
}
```

### Get Product

Get details of a specific product.

- **URL**: `/api/products/{product_id}`
- **Method**: `GET`
- **Auth required**: No

**Success Response**:

```json
{
  "id": 1,
  "hawker_id": 3,
  "name": "Chicken Rice",
  "description": "Delicious Singaporean chicken rice",
  "price": 5.5,
  "image_url": "https://example.com/images/chicken-rice.jpg",
  "is_available": true,
  "created_at": "2023-07-10T08:30:45",
  "updated_at": "2023-07-10T08:30:45"
}
```

### Update Product

Update a product (Hawker who owns the product only).

- **URL**: `/api/products/{product_id}`
- **Method**: `PUT`
- **Auth required**: Yes (Hawker role)

**Request Body**:

```json
{
  "name": "Hainanese Chicken Rice",
  "description": "Traditional Hainanese chicken rice",
  "price": 6.0,
  "image_url": "https://example.com/images/hainanese-chicken-rice.jpg",
  "is_available": true
}
```

**Success Response**:

```json
{
  "id": 1,
  "hawker_id": 3,
  "name": "Hainanese Chicken Rice",
  "description": "Traditional Hainanese chicken rice",
  "price": 6.0,
  "image_url": "https://example.com/images/hainanese-chicken-rice.jpg",
  "is_available": true,
  "created_at": "2023-07-10T08:30:45",
  "updated_at": "2023-07-15T16:45:20"
}
```

### Delete Product

Delete a product (Hawker who owns the product only).

- **URL**: `/api/products/{product_id}`
- **Method**: `DELETE`
- **Auth required**: Yes (Hawker role)

**Success Response**:

```json
{
  "message": "Product deleted successfully"
}
```

## Orders

### Create Order

Create a new order (Customer only).

- **URL**: `/api/orders`
- **Method**: `POST`
- **Auth required**: Yes
- **Note**: Orders can only be placed before 2 PM (configured cutoff time)

**Request Body**:

```json
{
  "items": [
    {
      "product_id": 1,
      "quantity": 2
    },
    {
      "product_id": 3,
      "quantity": 1
    }
  ],
  "delivery_address": "456 Main St",
  "delivery_latitude": 1.3421,
  "delivery_longitude": 103.8765,
  "delivery_instructions": "Leave at the door",
  "delivery_time_window_start": "2023-07-16T17:00:00",
  "delivery_time_window_end": "2023-07-16T19:00:00"
}
```

**Success Response**:

```json
{
  "success": true,
  "message": "Order created successfully",
  "order": {
    "id": 1,
    "customer_id": 2,
    "status": "pending",
    "total_amount": 15.5,
    "delivery_address": "456 Main St",
    "delivery_latitude": 1.3421,
    "delivery_longitude": 103.8765,
    "delivery_instructions": "Leave at the door",
    "delivery_time_window_start": "2023-07-16T17:00:00",
    "delivery_time_window_end": "2023-07-16T19:00:00",
    "created_at": "2023-07-15T13:30:45",
    "items": [
      {
        "product_id": 1,
        "product_name": "Chicken Rice",
        "quantity": 2,
        "price": 5.5
      },
      {
        "product_id": 3,
        "product_name": "Mee Goreng",
        "quantity": 1,
        "price": 4.5
      }
    ]
  }
}
```

**Error Response**:

- 400 Bad Request - Missing required fields or invalid items
- 403 Forbidden - Orders can only be placed before 2 PM

### List Orders

Get a list of orders for the current user.

- **URL**: `/api/orders`
- **Method**: `GET`
- **Auth required**: Yes
- **Query Parameters**:
  - `status` (optional): Filter by order status
  - `date` (optional): Filter by date (format: YYYY-MM-DD)

**Success Response**:

```json
[
  {
    "id": 1,
    "customer_id": 2,
    "hawker_id": 3,
    "status": "pending",
    "total_amount": 15.5,
    "delivery_address": "456 Main St",
    "delivery_latitude": 1.3421,
    "delivery_longitude": 103.8765,
    "delivery_instructions": "Leave at the door",
    "created_at": "2023-07-15T13:30:45",
    "items": [
      {
        "product_id": 1,
        "product_name": "Chicken Rice",
        "quantity": 2,
        "price": 5.5
      },
      {
        "product_id": 3,
        "product_name": "Mee Goreng",
        "quantity": 1,
        "price": 4.5
      }
    ]
  }
]
```

### Get Order

Get details of a specific order.

- **URL**: `/api/orders/{order_id}`
- **Method**: `GET`
- **Auth required**: Yes

**Success Response**:

```json
{
  "id": 1,
  "customer_id": 2,
  "hawker_id": 3,
  "status": "pending",
  "total_amount": 15.5,
  "delivery_address": "456 Main St",
  "delivery_latitude": 1.3421,
  "delivery_longitude": 103.8765,
  "delivery_instructions": "Leave at the door",
  "created_at": "2023-07-15T13:30:45",
  "items": [
    {
      "product_id": 1,
      "product_name": "Chicken Rice",
      "quantity": 2,
      "price": 5.5
    },
    {
      "product_id": 3,
      "product_name": "Mee Goreng",
      "quantity": 1,
      "price": 4.5
    }
  ]
}
```

### Update Order Status

Update the status of an order (Hawker or Customer depending on status).

- **URL**: `/api/orders/{order_id}/status`
- **Method**: `PATCH`
- **Auth required**: Yes

**Request Body**:

```json
{
  "status": "completed"
}
```

**Success Response**:

```json
{
  "success": true,
  "message": "Order status updated successfully",
  "order": {
    "id": 1,
    "status": "completed",
    "updated_at": "2023-07-16T18:45:30"
  }
}
```

### Cancel Order

Cancel an order.

- **URL**: `/api/orders/{order_id}/cancel`
- **Method**: `POST`
- **Auth required**: Yes

**Request Body**:

```json
{
  "reason": "Changed my mind"
}
```

**Success Response**:

```json
{
  "success": true,
  "message": "Order cancelled successfully",
  "order": {
    "id": 1,
    "status": "cancelled",
    "cancellation_reason": "Changed my mind",
    "cancelled_at": "2023-07-15T14:30:45"
  }
}
```

### Get Unassigned Orders

Get all unassigned orders (Admin only).

- **URL**: `/api/orders/unassigned`
- **Method**: `GET`
- **Auth required**: Yes (Admin role)

**Success Response**:

```json
{
  "success": true,
  "orders": [
    {
      "id": 5,
      "customer_id": 4,
      "status": "pending",
      "total_amount": 12.5,
      "delivery_address": "123 Orchard Rd",
      "delivery_latitude": 1.3041,
      "delivery_longitude": 103.8314,
      "created_at": "2023-07-15T11:30:45"
    }
  ]
}
```

### Get Assignment Status

Get the status of today's assignment batch.

- **URL**: `/api/orders/assignment/status`
- **Method**: `GET`
- **Auth required**: Yes

**Success Response**:

```json
{
  "success": true,
  "has_batch": true,
  "batch": {
    "batch_id": "batch_20230715_1a2b3c4d",
    "date": "2023-07-15",
    "status": "completed",
    "optimization_strategy": "balanced",
    "created_at": "2023-07-15T15:00:00",
    "completed_at": "2023-07-15T15:05:30",
    "result": {
      "total_orders": 25,
      "assigned_orders": 25,
      "total_hawkers": 8,
      "total_assignments": 42
    }
  }
}
```

## Deliveries

### Get Delivery Status

Get the current status of a delivery.

- **URL**: `/api/delivery/{order_id}/status`
- **Method**: `GET`
- **Auth required**: Yes

**Success Response**:

```json
{
  "order_id": 1,
  "status": "in_transit",
  "hawker_id": 3,
  "hawker_name": "John's Food",
  "estimated_arrival": "2023-07-16T18:30:00",
  "current_location": {
    "latitude": 1.3256,
    "longitude": 103.8542,
    "updated_at": "2023-07-16T18:15:30"
  },
  "updated_at": "2023-07-16T18:15:30"
}
```

### Update Delivery Status

Update the status of a delivery (Hawker only).

- **URL**: `/api/delivery/{order_id}/status`
- **Method**: `PUT`
- **Auth required**: Yes (Hawker role)

**Request Body**:

```json
{
  "status": "completed",
  "notes": "Delivered to customer"
}
```

**Success Response**:

```json
{
  "success": true,
  "message": "Delivery status updated successfully",
  "delivery": {
    "order_id": 1,
    "status": "completed",
    "notes": "Delivered to customer",
    "completed_at": "2023-07-16T18:45:30"
  }
}
```

### Get Delivery ETA

Get the estimated time of arrival for a delivery.

- **URL**: `/api/delivery/{order_id}/eta`
- **Method**: `GET`
- **Auth required**: Yes

**Success Response**:

```json
{
  "order_id": 1,
  "eta": "2023-07-16T18:30:00",
  "distance_remaining": 2500,
  "time_remaining": 900
}
```

### Track Delivery

Get real-time tracking information for a delivery.

- **URL**: `/api/delivery/{order_id}/track`
- **Method**: `GET`
- **Auth required**: Yes

**Success Response**:

```json
{
  "order_id": 1,
  "status": "in_transit",
  "hawker_location": {
    "latitude": 1.3256,
    "longitude": 103.8542,
    "updated_at": "2023-07-16T18:15:30"
  },
  "delivery_location": {
    "latitude": 1.3421,
    "longitude": 103.8765
  },
  "estimated_arrival": "2023-07-16T18:30:00",
  "distance_remaining": 2500,
  "time_remaining": 900
}
```

## Payments

### Create Payment

Create a new payment for an order.

- **URL**: `/api/payments`
- **Method**: `POST`
- **Auth required**: Yes

**Request Body**:

```json
{
  "order_id": 1,
  "payment_method": "credit_card",
  "amount": 15.5,
  "currency": "SGD",
  "payment_details": {
    "card_number": "4111111111111111",
    "expiry_month": 12,
    "expiry_year": 2025,
    "cvv": "123"
  }
}
```

**Success Response**:

```json
{
  "success": true,
  "message": "Payment processed successfully",
  "payment": {
    "id": 1,
    "order_id": 1,
    "payment_method": "credit_card",
    "amount": 15.5,
    "currency": "SGD",
    "status": "completed",
    "transaction_id": "txn_1234567890",
    "created_at": "2023-07-15T14:30:45"
  }
}
```

### Get Payment

Get details of a payment.

- **URL**: `/api/payments/{payment_id}`
- **Method**: `GET`
- **Auth required**: Yes

**Success Response**:

```json
{
  "id": 1,
  "order_id": 1,
  "payment_method": "credit_card",
  "amount": 15.5,
  "currency": "SGD",
  "status": "completed",
  "transaction_id": "txn_1234567890",
  "created_at": "2023-07-15T14:30:45",
  "updated_at": "2023-07-15T14:30:45"
}
```

### List Payments

Get a list of payments for the current user.

- **URL**: `/api/payments`
- **Method**: `GET`
- **Auth required**: Yes
- **Query Parameters**:
  - `status` (optional): Filter by payment status
  - `order_id` (optional): Filter by order ID

**Success Response**:

```json
[
  {
    "id": 1,
    "order_id": 1,
    "payment_method": "credit_card",
    "amount": 15.5,
    "currency": "SGD",
    "status": "completed",
    "transaction_id": "txn_1234567890",
    "created_at": "2023-07-15T14:30:45"
  },
  {
    "id": 2,
    "order_id": 3,
    "payment_method": "credit_card",
    "amount": 12.0,
    "currency": "SGD",
    "status": "completed",
    "transaction_id": "txn_0987654321",
    "created_at": "2023-07-16T10:15:20"
  }
]
```

### Refund Payment

Request a refund for a payment.

- **URL**: `/api/payments/{payment_id}/refund`
- **Method**: `POST`
- **Auth required**: Yes

**Request Body**:

```json
{
  "amount": 15.5,
  "reason": "Order cancelled"
}
```

**Success Response**:

```json
{
  "success": true,
  "message": "Refund processed successfully",
  "refund": {
    "id": 1,
    "payment_id": 1,
    "amount": 15.5,
    "status": "completed",
    "transaction_id": "ref_1234567890",
    "reason": "Order cancelled",
    "created_at": "2023-07-15T15:30:45"
  }
}
```

## Location

### Update User Location

Update the current user's location.

- **URL**: `/api/location`
- **Method**: `PUT`
- **Auth required**: Yes

**Request Body**:

```json
{
  "latitude": 1.3421,
  "longitude": 103.8765
}
```

**Success Response**:

```json
{
  "success": true,
  "message": "Location updated successfully",
  "location": {
    "latitude": 1.3421,
    "longitude": 103.8765,
    "updated_at": "2023-07-16T18:15:30"
  }
}
```

### Get Nearby Hawkers

Get a list of hawkers near the specified location.

- **URL**: `/api/location/nearby-hawkers`
- **Method**: `GET`
- **Auth required**: No
- **Query Parameters**:
  - `latitude` (required): Latitude of the location
  - `longitude` (required): Longitude of the location
  - `radius` (optional): Search radius in meters (default: 5000)

**Success Response**:

```json
[
  {
    "id": 3,
    "name": "John's Food",
    "business_name": "John's Delicious Food",
    "business_address": "123 Main St",
    "latitude": 1.3256,
    "longitude": 103.8542,
    "distance": 1200,
    "products_count": 15
  },
  {
    "id": 5,
    "name": "Mary's Kitchen",
    "business_name": "Mary's Home Kitchen",
    "business_address": "456 Orchard Rd",
    "latitude": 1.3041,
    "longitude": 103.8314,
    "distance": 2500,
    "products_count": 10
  }
]
```

### Get Distance Matrix

Calculate distance and travel time between multiple points.

- **URL**: `/api/location/distance-matrix`
- **Method**: `POST`
- **Auth required**: Yes

**Request Body**:

```json
{
  "origins": [
    {
      "latitude": 1.3256,
      "longitude": 103.8542
    }
  ],
  "destinations": [
    {
      "latitude": 1.3421,
      "longitude": 103.8765
    },
    {
      "latitude": 1.3041,
      "longitude": 103.8314
    }
  ]
}
```

**Success Response**:

```json
{
  "success": true,
  "matrix": [
    [
      {
        "distance": 2500,
        "duration": 900,
        "duration_in_traffic": 1200
      },
      {
        "distance": 3500,
        "duration": 1200,
        "duration_in_traffic": 1500
      }
    ]
  ]
}
```

### Get Geocode

Convert address to coordinates or coordinates to address.

- **URL**: `/api/location/geocode`
- **Method**: `GET`
- **Auth required**: No
- **Query Parameters**:
  - `address` (optional): Address to geocode
  - `latitude` and `longitude` (optional): Coordinates to reverse geocode

**Success Response (Geocode)**:

```json
{
  "success": true,
  "result": {
    "latitude": 1.3421,
    "longitude": 103.8765,
    "formatted_address": "456 Main St, Singapore 123456"
  }
}
```

**Success Response (Reverse Geocode)**:

```json
{
  "success": true,
  "result": {
    "latitude": 1.3421,
    "longitude": 103.8765,
    "formatted_address": "456 Main St, Singapore 123456",
    "street": "Main St",
    "building_number": "456",
    "postal_code": "123456",
    "country": "Singapore"
  }
}
```

## Error Responses

All endpoints may return the following error responses:

- **401 Unauthorized**:

  ```json
  {
    "error": "Missing or invalid authentication token"
  }
  ```

- **403 Forbidden**:

  ```json
  {
    "error": "You do not have permission to perform this action"
  }
  ```

- **404 Not Found**:

  ```json
  {
    "error": "Resource not found"
  }
  ```

- **500 Internal Server Error**:
  ```json
  {
    "error": "An internal server error occurred"
  }
  ```
