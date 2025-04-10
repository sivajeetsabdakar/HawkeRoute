# HawkeRoute API Documentation

## Server Configuration

### Base URL
```
https://api.hawkeroute.com
```
All API endpoints should be prefixed with this base URL.

### CORS
The server is configured to accept requests from allowed origins. Frontend developers should ensure their application's domain is added to the allowed origins list.

### Authentication

#### Session-based Authentication
1. Login endpoint:
```
POST /api/auth/login
```
Request body:
```json
{
  "username": "string",
  "password": "string"
}
```
Response:
```json
{
  "success": true,
  "user": {
    "id": number,
    "username": "string",
    "role": "string"
  }
}
```

2. Logout endpoint:
```
POST /api/auth/logout
```

3. Get current user:
```
GET /api/auth/me
```

The server uses HTTP-only cookies for session management. After successful login, all subsequent requests will automatically include the session cookie.

#### WebSocket Authentication
WebSocket connections are automatically authenticated using the same session cookie. Ensure you enable credentials in your Socket.IO client configuration:

```javascript
const socket = io('https://api.hawkeroute.com', {
  withCredentials: true
});
```

## WebSocket API

### Connection

The application uses Socket.IO for real-time communication. Connect to the WebSocket server using:

```javascript
const socket = io();
```

### Authentication

All WebSocket connections require authentication. The server will automatically authenticate the connection using the session cookie.

### Events

#### Connection Events

| Event | Description | Data |
|-------|-------------|------|
| `connect` | Emitted when client connects to server | None |
| `disconnect` | Emitted when client disconnects from server | None |
| `connected` | Emitted by server when client successfully connects | `{ user_id: number, username: string }` |

#### Order Tracking Events

| Event | Direction | Description | Data |
|-------|-----------|-------------|------|
| `join_order_tracking` | Client → Server | Join an order tracking room | `{ order_id: number }` |
| `leave_order_tracking` | Client → Server | Leave an order tracking room | `{ order_id: number }` |
| `tracking_joined` | Server → Client | Confirmation of joining tracking room | `{ order_id: number }` |
| `tracking_left` | Server → Client | Confirmation of leaving tracking room | `{ order_id: number }` |

#### Location Events

| Event | Direction | Description | Data |
|-------|-----------|-------------|------|
| `location_update` | Client → Server | Update user's location | `{ latitude: number, longitude: number, address?: string }` |
| `location_update` | Server → Client | Location update notification | `{ user_id: number, username: string, latitude: number, longitude: number, address?: string, updated_at: string }` |

#### Order Status Events

| Event | Direction | Description | Data |
|-------|-----------|-------------|------|
| `order_status_update` | Client → Server | Update order status | `{ order_id: number, status: string }` |
| `order_status_update` | Server → Client | Order status update notification | `{ order_id: number, status: string, updated_by: string, updated_at: string }` |

#### Route Events

| Event | Direction | Description | Data |
|-------|-----------|-------------|------|
| `route_update` | Client → Server | Request route update | None |
| `route_update` | Server → Client | Route update notification | `{ hawker_location: { lat: number, lng: number, address: string }, route: Array<{ order_id: number, lat: number, lng: number, address: string, eta: string }>, total_distance: number, total_duration: number, estimated_completion: string }` |

#### ETA Events

| Event | Direction | Description | Data |
|-------|-----------|-------------|------|
| `eta_update` | Server → Client | ETA update notification | `{ order_id: number, eta: string, updated_at: string }` |

## REST API Endpoints

### Notifications

#### Get Notification Preferences

```
GET /api/notifications/preferences
```

**Response:**
```json
{
  "success": true,
  "preferences": {
    "order_created": true,
    "order_confirmed": true,
    "order_preparing": true,
    "order_ready": true,
    "order_delivered": true,
    "order_cancelled": true,
    "account_updates": true,
    "promotions": true,
    "email_notifications": true,
    "push_notifications": true,
    "sms_notifications": false
  }
}
```

#### Update Notification Preferences

```
POST /api/notifications/preferences
```

**Request Body:**
```json
{
  "preferences": {
    "order_created": true,
    "order_confirmed": true,
    "order_preparing": true,
    "order_ready": true,
    "order_delivered": true,
    "order_cancelled": true,
    "account_updates": true,
    "promotions": true,
    "email_notifications": true,
    "push_notifications": true,
    "sms_notifications": false
  }
}
```

**Response:**
```json
{
  "success": true,
  "message": "Notification preferences updated successfully"
}
```

#### Get Notification History

```
GET /api/notifications/history
```

**Response:**
```json
{
  "success": true,
  "notifications": [
    {
      "id": 1,
      "type": "order_status",
      "title": "Order Confirmed",
      "message": "Your order #123 has been confirmed",
      "data": {
        "order_id": 123,
        "status": "confirmed"
      },
      "read": false,
      "created_at": "2023-11-15T10:30:00Z"
    }
  ]
}
```

#### Mark Notifications as Read

```
POST /api/notifications/mark-read
```

**Request Body:**
```json
{
  "notification_ids": [1, 2, 3]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Notifications marked as read"
}
```

### Location

#### Update User Location

```
POST /api/location/update
```

**Request Body:**
```json
{
  "latitude": 1.3521,
  "longitude": 103.8198,
  "address": "123 Main St, Singapore"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Location updated successfully"
}
```

#### Get User Location

```
GET /api/location/{user_id}
```

**Response:**
```json
{
  "success": true,
  "user_id": 1,
  "username": "johndoe",
  "latitude": 1.3521,
  "longitude": 103.8198,
  "address": "123 Main St, Singapore"
}
```

### Route

#### Optimize Route

```
POST /api/route/optimize
```

**Request Body:**
```json
{
  "date": "2023-11-15",
  "strategy": "distance",
  "time_window": 8,
  "return_to_start": true
}
```

**Response:**
```json
{
  "success": true,
  "hawker_location": {
    "lat": 1.3521,
    "lng": 103.8198,
    "address": "123 Main St, Singapore"
  },
  "route": [
    {
      "order_id": 123,
      "lat": 1.3521,
      "lng": 103.8198,
      "address": "123 Main St, Singapore",
      "eta": "2023-11-15T11:30:00Z"
    }
  ],
  "total_distance": 5000,
  "total_duration": 1800,
  "estimated_completion": "2023-11-15T12:00:00Z"
}
```

#### Get Current Route

```
GET /api/route/current
```

**Response:**
```json
{
  "success": true,
  "hawker_location": {
    "lat": 1.3521,
    "lng": 103.8198,
    "address": "123 Main St, Singapore"
  },
  "route": [
    {
      "order_id": 123,
      "lat": 1.3521,
      "lng": 103.8198,
      "address": "123 Main St, Singapore",
      "eta": "2023-11-15T11:30:00Z"
    }
  ],
  "total_distance": 5000,
  "total_duration": 1800,
  "estimated_completion": "2023-11-15T12:00:00Z"
}
```

#### Save Route

```
POST /api/route/save
```

**Response:**
```json
{
  "success": true,
  "message": "Route saved successfully"
}
```

### ETA

#### Update ETA

```
POST /api/eta/update/{order_id}
```

**Request Body:**
```json
{
  "eta": "2023-11-15T11:30:00Z"
}
```

**Response:**
```json
{
  "success": true,
  "message": "ETA updated successfully"
}
```

#### Get ETA

```
GET /api/eta/{order_id}
```

**Response:**
```json
{
  "success": true,
  "order_id": 123,
  "eta": "2023-11-15T11:30:00Z",
  "distance": 5000,
  "duration": 1800
}
```

## Implementation Guide

### WebSocket Integration

1. Install Socket.IO client:
   ```bash
   npm install socket.io-client
   ```

2. Connect to the WebSocket server:
   ```javascript
   import { io } from 'socket.io-client';
   
   const socket = io();
   
   socket.on('connect', () => {
     console.log('Connected to server');
   });
   
   socket.on('connected', (data) => {
     console.log('Connected as user:', data.username);
   });
   ```

3. Join order tracking:
   ```javascript
   function joinOrderTracking(orderId) {
     socket.emit('join_order_tracking', { order_id: orderId });
   }
   
   socket.on('tracking_joined', (data) => {
     console.log('Joined tracking for order:', data.order_id);
   });
   ```

4. Update location:
   ```javascript
   function updateLocation(latitude, longitude, address = null) {
     const data = {
       latitude: latitude,
       longitude: longitude
     };
     if (address) {
       data.address = address;
     }
     socket.emit('location_update', data);
   }
   
   socket.on('location_update', (data) => {
     console.log('Location update:', data);
     // Update UI with new location
   });
   ```

5. Update order status:
   ```javascript
   function updateOrderStatus(orderId, status) {
     socket.emit('order_status_update', {
       order_id: orderId,
       status: status
     });
   }
   
   socket.on('order_status_update', (data) => {
     console.log('Order status update:', data);
     // Update UI with new status
   });
   ```

6. Request route update:
   ```javascript
   function requestRouteUpdate() {
     socket.emit('route_update');
   }
   
   socket.on('route_update', (data) => {
     console.log('Route update:', data);
     // Update UI with new route
   });
   ```

7. Handle ETA updates:
   ```javascript
   socket.on('eta_update', (data) => {
     console.log('ETA update:', data);
     // Update UI with new ETA
   });
   ```

### REST API Integration

1. Get notification preferences:
   ```javascript
   async function getNotificationPreferences() {
     const response = await fetch('/api/notifications/preferences');
     const data = await response.json();
     if (data.success) {
       return data.preferences;
     }
     throw new Error(data.message);
   }
   ```

2. Update notification preferences:
   ```javascript
   async function updateNotificationPreferences(preferences) {
     const response = await fetch('/api/notifications/preferences', {
       method: 'POST',
       headers: {
         'Content-Type': 'application/json'
       },
       body: JSON.stringify({ preferences })
     });
     const data = await response.json();
     if (data.success) {
       return data;
     }
     throw new Error(data.message);
   }
   ```

3. Update location:
   ```javascript
   async function updateLocation(latitude, longitude, address = null) {
     const response = await fetch('/api/location/update', {
       method: 'POST',
       headers: {
         'Content-Type': 'application/json'
       },
       body: JSON.stringify({
         latitude,
         longitude,
         address
       })
     });
     const data = await response.json();
     if (data.success) {
       return data;
     }
     throw new Error(data.message);
   }
   ```

4. Optimize route:
   ```javascript
   async function optimizeRoute(date, strategy = 'distance', timeWindow = 8, returnToStart = true) {
     const response = await fetch('/api/route/optimize', {
       method: 'POST',
       headers: {
         'Content-Type': 'application/json'
       },
       body: JSON.stringify({
         date,
         strategy,
         time_window: timeWindow,
         return_to_start: returnToStart
       })
     });
     const data = await response.json();
     if (data.success) {
       return data;
     }
     throw new Error(data.message);
   }
   ```

5. Update ETA:
   ```javascript
   async function updateETA(orderId, eta) {
     const response = await fetch(`/api/eta/update/${orderId}`, {
       method: 'POST',
       headers: {
         'Content-Type': 'application/json'
       },
       body: JSON.stringify({ eta })
     });
     const data = await response.json();
     if (data.success) {
       return data;
     }
     throw new Error(data.message);
   }
   ```

## Error Handling

All API endpoints return a consistent error format:

```json
{
  "success": false,
  "message": "Error message describing what went wrong"
}
```

Common HTTP status codes:
- 200: Success
- 400: Bad Request (invalid input)
- 401: Unauthorized (not authenticated)
- 403: Forbidden (not authorized)
- 404: Not Found
- 500: Internal Server Error

## Authentication

All API endpoints and WebSocket connections require authentication. The application uses session-based authentication with cookies.

## Rate Limiting

API endpoints are rate-limited to prevent abuse. The default limit is 100 requests per minute per IP address.

## WebSocket Rooms

The application uses Socket.IO rooms for targeted message delivery:

- `user_{id}`: Personal room for each user
- `hawker_{id}`: Room for hawker-specific updates
- `order_{id}`: Room for order-specific updates
- `admin`: Room for admin-specific updates

## Order Status Flow

Orders follow this status flow:

1. `pending`: Order is created but not yet confirmed
2. `confirmed`: Order is confirmed by the hawker
3. `preparing`: Order is being prepared
4. `ready`: Order is ready for delivery
5. `delivering`: Order is being delivered
6. `delivered`: Order has been delivered
7. `cancelled`: Order has been cancelled

## Notification Types

The system supports the following notification types:

### Order Notifications
- `order_created`: New order received
- `order_confirmed`: Order confirmed by hawker
- `order_preparing`: Order being prepared
- `order_ready`: Order ready for delivery
- `order_delivered`: Order delivered
- `order_cancelled`: Order cancelled

### System Notifications
- `account_updates`: Account status updates
- `promotions`: Promotions and special offers

### Notification Methods
- `email_notifications`: Email notifications
- `push_notifications`: Push notifications
- `sms_notifications`: SMS notifications 