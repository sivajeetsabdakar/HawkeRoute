import axios from "axios";

const API_BASE_URL = "http://192.168.1.2:5000";

// Create axios instance with base URL
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Add request interceptor to include token in requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers["Authorization"] = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 (Unauthorized) and we haven't tried to refresh yet
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        // Get refresh token from storage
        const refreshToken = localStorage.getItem("refresh_token");
        if (!refreshToken) {
          // No refresh token, redirect to login
          window.location.href = "/login";
          return Promise.reject(error);
        }

        // Try to get new access token
        const response = await axios.post(
          `${API_BASE_URL}/api/auth/refresh`,
          {},
          {
            headers: {
              Authorization: `Bearer ${refreshToken}`,
            },
          }
        );

        // Save new access token
        const { access_token } = response.data;
        localStorage.setItem("access_token", access_token);

        // Update the original request with new token
        originalRequest.headers["Authorization"] = `Bearer ${access_token}`;

        // Retry the original request
        return api(originalRequest);
      } catch (refreshError) {
        // Clear tokens and redirect to login
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (userData) => api.post("/api/auth/register", userData),
  login: (credentials) => api.post("/api/auth/login", credentials),
  refreshToken: () => api.post("/api/auth/refresh"),
  getCurrentUser: () => api.get("/api/auth/me"),
  logout: () => api.post("/api/auth/logout"),
};

// Products API
export const productsAPI = {
  getAllProducts: (params) => api.get("/api/products", { params }),
  getProductById: (productId) => api.get(`/api/products/${productId}`),
  createProduct: (productData) => api.post("/api/products", productData),
  updateProduct: (productId, productData) =>
    api.put(`/api/products/${productId}`, productData),
  deleteProduct: (productId) => api.delete(`/api/products/${productId}`),
};

// Orders API
export const ordersAPI = {
  createOrder: (orderData) => api.post("/api/orders", orderData),
  getOrders: (params) => api.get("/api/orders", { params }),
  getOrderById: (orderId) => api.get(`/api/orders/${orderId}`),
  cancelOrder: (id) => api.post(`/api/orders/${id}/cancel`),
  updateOrderStatus: (orderId, status) =>
    api.patch(`/api/orders/${orderId}/status`, { status }),
  getHawkerOrders: (params) => api.get("/api/hawker/orders", { params }),
};

// Payments API
export const paymentsAPI = {
  initiatePayment: (orderId) =>
    api.post("/api/payments/initiate", { order_id: orderId }),
  verifyPayment: (paymentData) => api.post("/api/payments/verify", paymentData),
  recordCODPayment: (orderId) =>
    api.post("/api/payments/cod", { order_id: orderId }),
};

// Location API
export const locationAPI = {
  updateLocation: (locationData) =>
    api.post("/api/location/update", locationData),
  getCurrentLocation: () => api.get("/api/location/current"),
  getLocationHistory: (params) => api.get("/api/location/history", { params }),
  updateHawkerLocation: (locationData) =>
    api.put("/api/hawker/location", locationData),
  getNearbyHawkers: (latitude, longitude, radius = 5000) =>
    api.get(`/api/location/nearby-hawkers`, {
      params: { latitude, longitude, radius },
    }),
  getNearbyHawkers: (params) => api.get("/api/location/nearby-hawkers", { params }),
};

// Hawker API
export const hawkerAPI = {
  getProfile: (hawkerId) => api.get(`/api/hawker/profile/${hawkerId}`),
  getProducts: (hawkerId) => api.get(`/api/hawker/products/${hawkerId}`),
};

// Delivery Tracking API
export const deliveryAPI = {
  trackHawker: (hawkerId) => api.get(`/api/delivery/track/${hawkerId}`),
  getOptimizedRoute: () => api.get("/api/hawker/route"),
};

export default api;
