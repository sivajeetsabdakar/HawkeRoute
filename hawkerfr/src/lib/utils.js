import { jwtDecode } from "jwt-decode";
import { format, parseISO } from "date-fns";

// Format currency to display
export const formatCurrency = (amount, currency = "INR") => {
  return new Intl.NumberFormat("en-IN", {
    style: "currency",
    currency: currency,
  }).format(amount);
};

// Format date
export const formatDate = (dateString, formatStr = "PPP") => {
  if (!dateString) return "";
  return format(parseISO(dateString), formatStr);
};

// Format time
export const formatTime = (dateString, formatStr = "p") => {
  if (!dateString) return "";
  return format(parseISO(dateString), formatStr);
};

// Format date and time
export const formatDateTime = (dateString, formatStr = "PPp") => {
  if (!dateString) return "";
  return format(parseISO(dateString), formatStr);
};

// Decode JWT token
export const decodeToken = (token) => {
  try {
    return jwtDecode(token);
  } catch (error) {
    return null;
  }
};

// Check if the user is authenticated
export const isAuthenticated = () => {
  const token = localStorage.getItem("access_token");
  if (!token) return false;

  try {
    const decoded = jwtDecode(token);
    const currentTime = Date.now() / 1000;

    return decoded.exp > currentTime;
  } catch (error) {
    return false;
  }
};

// Check if the user has a specific role
export const hasRole = (role) => {
  const token = localStorage.getItem("access_token");
  if (!token) return false;

  try {
    const decoded = jwtDecode(token);
    return decoded.role === role;
  } catch (error) {
    return false;
  }
};

// Truncate text
export const truncateText = (text, maxLength = 50) => {
  if (!text) return "";
  if (text.length <= maxLength) return text;

  return text.substring(0, maxLength) + "...";
};

// Validate email
export const isValidEmail = (email) => {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return regex.test(email);
};

// Validate phone number (simple validation, assumes 10-digit number)
export const isValidPhone = (phone) => {
  const regex = /^\d{10}$/;
  return regex.test(phone);
};

// Get user ID from token
export const getUserId = () => {
  const token = localStorage.getItem("access_token");
  if (!token) return null;

  try {
    const decoded = jwtDecode(token);
    return decoded.id;
  } catch (error) {
    return null;
  }
};

// Get error message from API error response
export const getErrorMessage = (error) => {
  if (error.response && error.response.data && error.response.data.error) {
    return error.response.data.error;
  }

  return error.message || "An unexpected error occurred";
};

export default {
  formatCurrency,
  formatDate,
  formatTime,
  formatDateTime,
  decodeToken,
  isAuthenticated,
  hasRole,
  truncateText,
  isValidEmail,
  isValidPhone,
  getUserId,
  getErrorMessage,
};
