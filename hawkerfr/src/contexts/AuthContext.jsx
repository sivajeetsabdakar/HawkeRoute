"use client";

import { createContext, useContext, useState, useEffect } from "react";
import { authAPI } from "@/lib/api";
import { decodeToken, isAuthenticated } from "@/lib/utils";

// Create the context
const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Load the user data when the app starts
  useEffect(() => {
    const loadUser = async () => {
      try {
        // Check if the user is authenticated
        if (!isAuthenticated()) {
          setLoading(false);
          return;
        }

        // Get the current user data
        const response = await authAPI.getCurrentUser();
        setUser(response.data);
      } catch (error) {
        console.error("Error loading user:", error);
        // Clear tokens if there's an authentication error
        if (error.response && error.response.status === 401) {
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
        }
        setError(error);
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, []);

  // Register a new user
  const register = async (userData) => {
    try {
      setLoading(true);
      const response = await authAPI.register(userData);

      // Save tokens to local storage
      localStorage.setItem("access_token", response.data.access_token);
      localStorage.setItem("refresh_token", response.data.refresh_token);

      // Set user data
      setUser(response.data.user);

      return response.data;
    } catch (error) {
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Login user
  const login = async (credentials) => {
    try {
      setLoading(true);
      const response = await authAPI.login(credentials);

      // Save tokens to local storage
      localStorage.setItem("access_token", response.data.access_token);
      localStorage.setItem("refresh_token", response.data.refresh_token);

      // Set user data
      setUser(response.data.user);

      return response.data;
    } catch (error) {
      setError(error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // Logout user
  const logout = async () => {
    try {
      setLoading(true);
      await authAPI.logout();
    } catch (error) {
      console.error("Error during logout:", error);
    } finally {
      // Clear user data and tokens
      setUser(null);
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      setLoading(false);
    }
  };

  // Check if the user has a specific role
  const hasRole = (role) => {
    if (!user) return false;
    return user.role === role;
  };

  // The value that will be provided to consumers of this context
  const value = {
    user,
    loading,
    error,
    register,
    login,
    logout,
    isAuthenticated: !!user,
    hasRole,
    isCustomer: user?.role === "customer",
    isHawker: user?.role === "hawker",
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};

// Custom hook to use the auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};

export default AuthContext;
