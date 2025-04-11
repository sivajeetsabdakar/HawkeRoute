# HawkeRoute API Documentation

## Overview

HawkeRoute is a platform that connects customers with hawkers (street vendors) for food delivery. The API is designed to support two main user types:

1. **Customers**: Can browse products, place orders, and track deliveries
2. **Hawkers**: Can list products, manage orders, and get optimized delivery routes

## Base URL

All API endpoints are prefixed with:
```
https://api.hawkeroute.com
```

## Authentication

All API endpoints except registration and login require authentication using JWT tokens.

### Authentication Endpoints

#### Register a User

```
POST /api/auth/register
```

**Request Body:**
```json
{
  "name": "User Name",
  "email": "user@example.com",
  "phone": "1234567890",
  "password": "password123",
  "role": "customer" // or "hawker"
}
```

**For Hawkers, additional fields:**
```json
{
  "business_name": "Hawker Business Name",
  "business_address": "123 Street Name",
  "latitude": 1.2345,
  "longitude": 6.7890
}
```

**Response:**
```json
{
  "message": "Registration successful",
  "user": {
    "id": 1,
    "name": "User Name",
    "email": "user@example.com",
    "phone": "1234567890",
    "role": "customer",
    "is_active": true
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Login

```
POST /api/auth/login
```

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**Response:**
```json
{
  "message": "Login successful",
  "user": {
    "id": 1,
    "name": "User Name",
    "email": "user@example.com",
    "phone": "1234567890",
    "role": "customer",
    "is_active": true
  },
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Refresh Token

```
POST /api/auth/refresh
```

**Headers:**
```
Authorization: Bearer {refresh_token}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

#### Get Current User

```
GET /api/auth/me
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 1,
  "name": "User Name",
  "email": "user@example.com",
  "phone": "1234567890",
  "role": "customer",
  "is_active": true
}
```

#### Logout

```
POST /api/auth/logout
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "message": "Successfully logged out"
}
```

## Customer API Endpoints

### Products

#### Get All Products

```
GET /api/products
```

**Query Parameters:**
- `hawker_id` (optional): Filter products by hawker
- `is_available` (optional): Filter by availability (true/false)

**Response:**
```json
[
  {
    "id": 1,
    "hawker_id": 2,
    "name": "Product Name",
    "description": "Product Description",
    "price": 10.99,
    "image_url": "https://example.com/image.jpg",
    "is_available": true,
    "created_at": "2023-01-01T12:00:00Z",
    "updated_at": "2023-01-01T12:00:00Z"
  },
  // More products...
]
```

#### Get Product by ID

```
GET /api/products/{product_id}
```

**Response:**
```json
{
  "id": 1,
  "hawker_id": 2,
  "name": "Product Name",
  "description": "Product Description",
  "price": 10.99,
  "image_url": "https://example.com/image.jpg",
  "is_available": true,
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

### Orders

#### Create Order

```
POST /api/orders
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "hawker_id": 2,
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
  "delivery_address": "123 Customer Street",
  "delivery_latitude": 1.2345,
  "delivery_longitude": 6.7890,
  "delivery_instructions": "Leave at the door"
}
```

**Response:**
```json
{
  "id": 1,
  "customer_id": 1,
  "hawker_id": 2,
  "total_amount": 32.97,
  "delivery_address": "123 Customer Street",
  "delivery_latitude": 1.2345,
  "delivery_longitude": 6.7890,
  "delivery_instructions": "Leave at the door",
  "status": "pending",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z",
  "items": [
    {
      "id": 1,
      "order_id": 1,
      "product_id": 1,
      "quantity": 2,
      "price": 10.99
    },
    {
      "id": 2,
      "order_id": 1,
      "product_id": 3,
      "quantity": 1,
      "price": 11.00
    }
  ]
}
```

#### Get Orders

```
GET /api/orders
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `status` (optional): Filter by order status
- `date` (optional): Filter by date (YYYY-MM-DD)

**Response:**
```json
[
  {
    "id": 1,
    "customer_id": 1,
    "hawker_id": 2,
    "total_amount": 32.97,
    "delivery_address": "123 Customer Street",
    "delivery_latitude": 1.2345,
    "delivery_longitude": 6.7890,
    "delivery_instructions": "Leave at the door",
    "status": "confirmed",
    "created_at": "2023-01-01T12:00:00Z",
    "updated_at": "2023-01-01T12:00:00Z"
  },
  // More orders...
]
```

#### Get Order by ID

```
GET /api/orders/{order_id}
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 1,
  "customer_id": 1,
  "hawker_id": 2,
  "total_amount": 32.97,
  "delivery_address": "123 Customer Street",
  "delivery_latitude": 1.2345,
  "delivery_longitude": 6.7890,
  "delivery_instructions": "Leave at the door",
  "status": "confirmed",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z",
  "items": [
    {
      "id": 1,
      "order_id": 1,
      "product_id": 1,
      "quantity": 2,
      "price": 10.99
    },
    {
      "id": 2,
      "order_id": 1,
      "product_id": 3,
      "quantity": 1,
      "price": 11.00
    }
  ]
}
```

### Payments

#### Initiate Payment

```
POST /api/payments/initiate
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "order_id": 1
}
```

**Response:**
```json
{
  "order_id": "order_123456789",
  "amount": 3297,
  "currency": "INR",
  "key": "razorpay_key_id"
}
```

#### Verify Payment

```
POST /api/payments/verify
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "razorpay_payment_id": "pay_123456789",
  "razorpay_order_id": "order_123456789",
  "razorpay_signature": "signature"
}
```

**Response:**
```json
{
  "message": "Payment verified successfully",
  "payment": {
    "id": 1,
    "order_id": 1,
    "amount": 32.97,
    "payment_method": "razorpay",
    "status": "success",
    "transaction_id": "order_123456789",
    "created_at": "2023-01-01T12:00:00Z"
  },
  "order": {
    "id": 1,
    "customer_id": 1,
    "hawker_id": 2,
    "total_amount": 32.97,
    "status": "confirmed",
    "created_at": "2023-01-01T12:00:00Z"
  }
}
```

### Location

#### Update Location

```
POST /api/location/update
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "latitude": 1.2345,
  "longitude": 6.7890,
  "accuracy": 10,
  "speed": 5,
  "heading": 90,
  "location_type": "idle",
  "order_id": 1
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "user_id": 1,
    "latitude": 1.2345,
    "longitude": 6.7890,
    "accuracy": 10,
    "speed": 5,
    "heading": 90,
    "location_type": "idle",
    "order_id": 1,
    "created_at": "2023-01-01T12:00:00Z"
  }
}
```

#### Get Current Location

```
GET /api/location/current
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 1,
    "user_id": 1,
    "latitude": 1.2345,
    "longitude": 6.7890,
    "accuracy": 10,
    "speed": 5,
    "heading": 90,
    "location_type": "idle",
    "order_id": 1,
    "created_at": "2023-01-01T12:00:00Z"
  }
}
```

#### Get Location History

```
GET /api/location/history
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `start_time` (optional): Start time in ISO format
- `end_time` (optional): End time in ISO format
- `location_type` (optional): Filter by location type
- `order_id` (optional): Filter by order ID
- `limit` (optional): Maximum number of records to return (default: 100)

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1,
      "user_id": 1,
      "latitude": 1.2345,
      "longitude": 6.7890,
      "accuracy": 10,
      "speed": 5,
      "heading": 90,
      "location_type": "idle",
      "order_id": 1,
      "created_at": "2023-01-01T12:00:00Z"
    },
    // More location records...
  ]
}
```

### Delivery Tracking

#### Track Hawker

```
GET /api/delivery/track/{hawker_id}
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "hawker": {
    "id": 2,
    "name": "Hawker Business Name",
    "latitude": 1.2345,
    "longitude": 6.7890
  },
  "route": {
    "id": 1,
    "hawker_id": 2,
    "date": "2023-01-01",
    "waypoints": [
      {
        "id": 1,
        "route_id": 1,
        "order_id": 1,
        "latitude": 1.2345,
        "longitude": 6.7890,
        "sequence": 1,
        "status": "pending"
      },
      // More waypoints...
    ]
  },
  "order": {
    "id": 1,
    "customer_id": 1,
    "hawker_id": 2,
    "total_amount": 32.97,
    "delivery_address": "123 Customer Street",
    "delivery_latitude": 1.2345,
    "delivery_longitude": 6.7890,
    "delivery_instructions": "Leave at the door",
    "status": "delivering",
    "created_at": "2023-01-01T12:00:00Z"
  }
}
```

## Hawker API Endpoints

### Products

#### Create Product

```
POST /api/products
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "name": "Product Name",
  "description": "Product Description",
  "price": 10.99,
  "image_url": "https://example.com/image.jpg",
  "is_available": true
}
```

**Response:**
```json
{
  "id": 1,
  "hawker_id": 2,
  "name": "Product Name",
  "description": "Product Description",
  "price": 10.99,
  "image_url": "https://example.com/image.jpg",
  "is_available": true,
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

#### Update Product

```
PUT /api/products/{product_id}
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "name": "Updated Product Name",
  "description": "Updated Product Description",
  "price": 11.99,
  "image_url": "https://example.com/updated-image.jpg",
  "is_available": true
}
```

**Response:**
```json
{
  "id": 1,
  "hawker_id": 2,
  "name": "Updated Product Name",
  "description": "Updated Product Description",
  "price": 11.99,
  "image_url": "https://example.com/updated-image.jpg",
  "is_available": true,
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

#### Delete Product

```
DELETE /api/products/{product_id}
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "message": "Product deleted successfully"
}
```

### Orders

#### Get Hawker Orders

```
GET /api/hawker/orders
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Query Parameters:**
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10)
- `status` (optional): Filter by order status

**Response:**
```json
[
  {
    "id": 1,
    "customer_id": 1,
    "hawker_id": 2,
    "total_amount": 32.97,
    "delivery_address": "123 Customer Street",
    "delivery_latitude": 1.2345,
    "delivery_longitude": 6.7890,
    "delivery_instructions": "Leave at the door",
    "status": "confirmed",
    "created_at": "2023-01-01T12:00:00Z",
    "updated_at": "2023-01-01T12:00:00Z",
    "items": [
      {
        "id": 1,
        "order_id": 1,
        "product_id": 1,
        "quantity": 2,
        "price": 10.99
      },
      {
        "id": 2,
        "order_id": 1,
        "product_id": 3,
        "quantity": 1,
        "price": 11.00
      }
    ]
  },
  // More orders...
]
```

#### Update Order Status

```
PATCH /api/orders/{order_id}/status
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "status": "delivering"
}
```

**Valid Status Values:**
- `confirmed`
- `preparing`
- `delivering`
- `delivered`
- `cancelled`

**Response:**
```json
{
  "id": 1,
  "customer_id": 1,
  "hawker_id": 2,
  "total_amount": 32.97,
  "delivery_address": "123 Customer Street",
  "delivery_latitude": 1.2345,
  "delivery_longitude": 6.7890,
  "delivery_instructions": "Leave at the door",
  "status": "delivering",
  "created_at": "2023-01-01T12:00:00Z",
  "updated_at": "2023-01-01T12:00:00Z"
}
```

### Route Optimization

#### Get Optimized Route

```
GET /api/hawker/route
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Response:**
```json
{
  "id": 1,
  "hawker_id": 2,
  "date": "2023-01-01",
  "total_distance": 5.2,
  "total_time": 15,
  "waypoints": [
    {
      "id": 1,
      "route_id": 1,
      "order_id": 1,
      "latitude": 1.2345,
      "longitude": 6.7890,
      "sequence": 1,
      "status": "pending",
      "order": {
        "id": 1,
        "customer_id": 1,
        "hawker_id": 2,
        "total_amount": 32.97,
        "delivery_address": "123 Customer Street",
        "delivery_latitude": 1.2345,
        "delivery_longitude": 6.7890,
        "delivery_instructions": "Leave at the door",
        "status": "confirmed"
      }
    },
    // More waypoints...
  ]
}
```

### Location

#### Update Hawker Location

```
PUT /api/hawker/location
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "latitude": 1.2345,
  "longitude": 6.7890
}
```

**Response:**
```json
{
  "message": "Location updated successfully"
}
```

### Payments

#### Record Cash on Delivery Payment

```
POST /api/payments/cod
```

**Headers:**
```
Authorization: Bearer {access_token}
```

**Request Body:**
```json
{
  "order_id": 1
}
```

**Response:**
```json
{
  "message": "COD payment recorded successfully",
  "payment": {
    "id": 1,
    "order_id": 1,
    "amount": 32.97,
    "payment_method": "cod",
    "status": "success",
    "transaction_id": "cod_1_1234567890",
    "created_at": "2023-01-01T12:00:00Z"
  }
}
```

## WebSocket Events

### Delivery Tracking

Connect to the WebSocket endpoint:
```
ws://api.hawkeroute.com/delivery
```

#### Join Tracking Room

```javascript
socket.emit('join_tracking', { hawker_id: 2 });
```

#### Leave Tracking Room

```javascript
socket.emit('leave_tracking', { hawker_id: 2 });
```

#### Location Update Event

```javascript
socket.on('location_update', function(data) {
  console.log('Hawker location updated:', data);
  // data = {
  //   hawker_id: 2,
  //   latitude: 1.2345,
  //   longitude: 6.7890,
  //   timestamp: "2023-01-01T12:00:00Z"
  // }
});
```

## Error Handling

All API endpoints return appropriate HTTP status codes:

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `403`: Forbidden
- `404`: Not Found
- `409`: Conflict
- `500`: Internal Server Error

Error responses follow this format:

```json
{
  "error": "Error message description"
}
```

## Authentication Flow

1. Register a user with `/api/auth/register`
2. Login with `/api/auth/login` to get access and refresh tokens
3. Include the access token in the `Authorization` header for all API requests
4. When the access token expires, use the refresh token with `/api/auth/refresh` to get a new access token
5. Logout with `/api/auth/logout` to invalidate the tokens

## Testing

For testing purposes, you can use the following test accounts:

**Customer:**
- Email: customer@example.com
- Password: password123

**Hawker:**
- Email: hawker@example.com
- Password: password123

## Support

For API support, please contact:
- Email: api-support@hawkeroute.com
- Phone: +1234567890 