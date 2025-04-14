"use client";

import { useState, useEffect } from "react";
import { FiCheckCircle, FiXCircle, FiMapPin } from "react-icons/fi";
import Link from "next/link";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import StaticMap from "@/components/maps/StaticMap";
import { useAuth } from "@/contexts/AuthContext";
import { useCart } from "@/contexts/CartContext";
import { ordersAPI, productsAPI, hawkerAPI, locationAPI } from "@/lib/api";
import toast from "react-hot-toast";

/**
 * FrontendTest Component
 * 
 * This component is used to test various frontend functionalities of the HawkerRoute application.
 * It provides test panels for:
 * - Map rendering
 * - Toast notifications
 * - API calls
 * - Cart functionality
 * - Authentication
 */
export default function FrontendTest() {
  const { isAuthenticated, user, login, logout } = useAuth();
  const { cartItems, addToCart, removeFromCart, clearCart } = useCart();
  
  const [testResults, setTestResults] = useState({});
  const [loading, setLoading] = useState(false);
  const [coordinates, setCoordinates] = useState({
    latitude: 1.3521,
    longitude: 103.8198 // Default: Singapore coordinates
  });
  const [testProduct, setTestProduct] = useState(null);
  
  // Run initial tests on component mount
  useEffect(() => {
    // Check if key components are available
    const componentTests = {
      "StaticMap Component": !!StaticMap,
      "Button Component": !!Button,
      "Card Component": !!Card,
      "Auth Context": !!useAuth,
      "Cart Context": !!useCart,
      "API Module": !!(ordersAPI && productsAPI),
      "Toast Notification": !!toast
    };
    
    setTestResults(prev => ({
      ...prev,
      components: componentTests
    }));
    
    // Test browser APIs
    const browserTests = {
      "LocalStorage": !!window.localStorage,
      "Geolocation": !!navigator.geolocation,
      "Fetch API": !!window.fetch,
      "Session Storage": !!window.sessionStorage
    };
    
    setTestResults(prev => ({
      ...prev,
      browser: browserTests
    }));
    
    // Fetch a test product for cart testing
    fetchTestProduct();
  }, []);
  
  // Fetch a sample product for testing
  const fetchTestProduct = async () => {
    try {
      const response = await productsAPI.getAllProducts({ limit: 1 });
      
      if (response.data && Array.isArray(response.data) && response.data.length > 0) {
        setTestProduct(response.data[0]);
      } else if (response.data && response.data.status === "success" && Array.isArray(response.data.data) && response.data.data.length > 0) {
        setTestProduct(response.data.data[0]);
      } else {
        // Create mock product if no products are found
        setTestProduct({
          id: "test-product-1",
          name: "Test Product",
          price: 9.99,
          hawker_id: "test-hawker-1",
          hawker_name: "Test Hawker",
          image_url: "https://via.placeholder.com/150"
        });
      }
    } catch (error) {
      console.error("Error fetching test product:", error);
      // Create mock product if API fails
      setTestProduct({
        id: "test-product-1",
        name: "Test Product",
        price: 9.99,
        hawker_id: "test-hawker-1",
        hawker_name: "Test Hawker",
        image_url: "https://via.placeholder.com/150"
      });
    }
  };
  
  // Test map rendering with different coordinates
  const testMapWithCoordinates = () => {
    toast.success("Testing map with coordinates", {
      icon: "🗺️"
    });
    
    setCoordinates({
      latitude: parseFloat(coordinates.latitude) + (Math.random() * 0.02 - 0.01),
      longitude: parseFloat(coordinates.longitude) + (Math.random() * 0.02 - 0.01)
    });
  };
  
  // Test toast notifications
  const testToastNotifications = () => {
    toast.success("Success toast test", {
      icon: "✅"
    });
    
    setTimeout(() => {
      toast.error("Error toast test", {
        icon: "❌"
      });
    }, 1000);
    
    setTimeout(() => {
      toast.loading("Loading toast test");
    }, 2000);
  };
  
  // Test API calls
  const testAPIConnections = async () => {
    setLoading(true);
    const results = {};
    
    try {
      // Test products API
      const productsResponse = await productsAPI.getAllProducts({ limit: 1 });
      results.products = !!productsResponse.data;
    } catch (error) {
      results.products = false;
    }
    
    try {
      // Test hawkers API
      const hawkersResponse = await locationAPI.getNearbyHawkerss(1.3521, 103.8198, 5000);
      results.hawkers = !!hawkersResponse.data;
    } catch (error) {
      results.hawkers = false;
    }
    
    try {
      // Test location API if available
      if (locationAPI && locationAPI.getNearbyHawkers) {
        const locationResponse = await locationAPI.getNearbyHawkers({
          latitude: 1.3521,
          longitude: 103.8198,
          radius: 5000
        });
        results.location = !!locationResponse.data;
      } else {
        results.location = "API not available";
      }
    } catch (error) {
      results.location = false;
    }
    
    setTestResults(prev => ({
      ...prev,
      api: results
    }));
    
    setLoading(false);
    
    // Show toast with results
    if (Object.values(results).every(result => result === true || result === "API not available")) {
      toast.success("All API tests passed!", { duration: 3000 });
    } else {
      toast.error("Some API tests failed. Check results for details.", { duration: 3000 });
    }
  };
  
  // Test cart functionality
  const testCartFunctionality = () => {
    if (!testProduct) {
      toast.error("No test product available");
      return;
    }
    
    // Clear cart first
    clearCart();
    toast("Cart cleared for testing", { icon: "🛒" });
    
    // Add to cart
    setTimeout(() => {
      addToCart(testProduct);
      toast.success(`Added ${testProduct.name} to cart`);
    }, 1000);
    
    // Update quantity
    setTimeout(() => {
      addToCart(testProduct);
      toast.success(`Updated ${testProduct.name} quantity to 2`);
    }, 2000);
    
    // Remove from cart
    setTimeout(() => {
      removeFromCart(testProduct.id);
      toast.success(`Removed ${testProduct.name} from cart`);
    }, 3000);
  };
  
  // Get user's current location
  const testUserLocation = () => {
    if (!navigator.geolocation) {
      toast.error("Geolocation is not supported by your browser");
      return;
    }
    
    toast.loading("Getting your location...");
    
    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setCoordinates({ latitude, longitude });
        toast.dismiss();
        toast.success(`Location found: ${latitude.toFixed(6)}, ${longitude.toFixed(6)}`);
      },
      (error) => {
        toast.dismiss();
        toast.error(`Error getting location: ${error.message}`);
      }
    );
  };
  
  return (
    <div className="space-y-8 pb-12">
      <div className="border-b border-gray-200 pb-5 mb-5">
        <h1 className="text-3xl font-bold text-white">Frontend Test Suite</h1>
        <p className="mt-2 text-sm text-gray-800">
          Test various frontend functionalities of the HawkerRoute application
        </p>
      </div>
      
      {/* Environment Info */}
      <Card>
        <h2 className="text-xl font-semibold mb-4 text-black">Environment Information</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <p className="font-medium text-black">User Agent:</p>
            <p className="text-sm text-gray-800 break-words">{navigator.userAgent}</p>
          </div>
          <div>
            <p className="font-medium text-black">Screen Resolution:</p>
            <p className="text-sm text-gray-800">{window.innerWidth}x{window.innerHeight}</p>
          </div>
          <div>
            <p className="font-medium text-black">Authentication Status:</p>
            <p className="text-sm text-gray-800">
              {isAuthenticated ? (
                <span className="text-green-600 flex items-center font-medium">
                  <FiCheckCircle className="mr-1" /> Authenticated as {user?.name || user?.email || "User"}
                </span>
              ) : (
                <span className="text-red-600 flex items-center font-medium">
                  <FiXCircle className="mr-1" /> Not authenticated
                </span>
              )}
            </p>
          </div>
          <div>
            <p className="font-medium text-black">Cart Items:</p>
            <p className="text-sm text-gray-800">{cartItems.length} items in cart</p>
          </div>
        </div>
      </Card>
      
      {/* Component Tests */}
      <Card>
        <h2 className="text-xl font-semibold mb-4 text-black">Component Tests</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {testResults.components && Object.entries(testResults.components).map(([test, result]) => (
            <div key={test} className="flex items-center justify-between p-2 border-b border-gray-100">
              <span className="text-gray-900 ">{test}</span>
              {result ? (
                <span className="text-green-600 flex items-center font-medium">
                  <FiCheckCircle className="mr-1" /> Passed
                </span>
              ) : (
                <span className="text-red-600 flex items-center font-medium">
                  <FiXCircle className="mr-1" /> Failed
                </span>
              )}
            </div>
          ))}
        </div>
      </Card>
      
      {/* Browser API Tests */}
      <Card>
        <h2 className="text-xl font-semibold mb-4 text-black">Browser API Tests</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {testResults.browser && Object.entries(testResults.browser).map(([test, result]) => (
            <div key={test} className="flex items-center justify-between p-2 border-b border-gray-100">
              <span className="text-gray-900">{test}</span>
              {result ? (
                <span className="text-green-600 flex items-center font-medium">
                  <FiCheckCircle className="mr-1" /> Available
                </span>
              ) : (
                <span className="text-red-600 flex items-center font-medium">
                  <FiXCircle className="mr-1" /> Not Available
                </span>
              )}
            </div>
          ))}
        </div>
      </Card>
      
      {/* API Connection Tests */}
      <Card>
        <h2 className="text-xl font-semibold mb-4 text-black">API Connection Tests</h2>
        {testResults.api ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {Object.entries(testResults.api).map(([api, result]) => (
              <div key={api} className="flex items-center justify-between p-2 border-b border-gray-100">
                <span className="text-gray-900">{api} API</span>
                {result === true ? (
                  <span className="text-green-600 flex items-center font-medium">
                    <FiCheckCircle className="mr-1" /> Connected
                  </span>
                ) : result === "API not available" ? (
                  <span className="text-yellow-600 font-medium">Not Available</span>
                ) : (
                  <span className="text-red-600 flex items-center font-medium">
                    <FiXCircle className="mr-1" /> Failed
                  </span>
                )}
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-900">No API tests run yet</p>
        )}
        <div className="mt-4">
          <Button onClick={testAPIConnections} disabled={loading}>
            {loading ? "Testing..." : "Test API Connections"}
          </Button>
        </div>
      </Card>
      
      {/* Map Test */}
      <Card>
        <h2 className="text-xl font-semibold mb-4 text-black">Map Component Test</h2>
        <div className="aspect-square md:aspect-video mb-4">
          <StaticMap 
            latitude={coordinates.latitude} 
            longitude={coordinates.longitude}
            title="Test Location"
            className="w-full h-full"
          />
        </div>
        <div className="flex flex-wrap gap-2">
          <Button onClick={testMapWithCoordinates}>
            Test with Random Coordinates
          </Button>
          <Button onClick={testUserLocation} variant="outline">
            <FiMapPin className="mr-2" /> Use My Location
          </Button>
        </div>
        <div className="mt-4 text-sm text-gray-900">
          <p>Current Coordinates: {coordinates.latitude}, {coordinates.longitude}</p>
        </div>
      </Card>
      
      {/* Toast Test */}
      <Card>
        <h2 className="text-xl font-semibold mb-4 text-black">Toast Notifications Test</h2>
        <p className="mb-4 text-sm text-gray-900">
          Test various toast notification styles and behaviors
        </p>
        <Button onClick={testToastNotifications}>
          Test Toast Notifications
        </Button>
      </Card>
      
      {/* Cart Test */}
      <Card>
        <h2 className="text-xl font-semibold mb-4 text-black">Cart Functionality Test</h2>
        <p className="mb-4 text-sm text-gray-900">
          Test adding, updating, and removing items from the cart
        </p>
        {testProduct ? (
          <div className="mb-4">
            <p className="font-medium">Test Product:</p>
            <p className="text-sm text-gray-900">{testProduct.name} - ${testProduct.price}</p>
          </div>
        ) : (
          <p className="text-gray-900 mb-4">Loading test product...</p>
        )}
        <Button onClick={testCartFunctionality} disabled={!testProduct}>
          Test Cart Workflow
        </Button>
      </Card>
      
      {/* Navigation Links */}
      <Card>
        <h2 className="text-xl font-semibold mb-4 text-black">Navigation Test</h2>
        <p className="mb-4 text-sm text-gray-900">
          Test navigation to key pages in the application
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
          <Link href="/">
            <Button variant="outline" className="w-full">Home</Button>
          </Link>
          <Link href="/hawkers">
            <Button variant="outline" className="w-full">Hawkers</Button>
          </Link>
          <Link href="/orders">
            <Button variant="outline" className="w-full">Orders</Button>
          </Link>
          <Link href="/cart">
            <Button variant="outline" className="w-full">Cart</Button>
          </Link>
          <Link href="/profile">
            <Button variant="outline" className="w-full">Profile</Button>
          </Link>
          <Link href="/login">
            <Button variant="outline" className="w-full">Login</Button>
          </Link>
        </div>
      </Card>
      
      <div className="text-center text-sm text-black pt-8">
        <p>HawkerRoute Frontend Test Suite</p>
        <p>Current time: {new Date().toLocaleString()}</p>
      </div>
    </div>
  );
} 