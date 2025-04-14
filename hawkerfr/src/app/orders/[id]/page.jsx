"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import {
  FiArrowLeft,
  FiClock,
  FiCheckCircle,
  FiTruck,
  FiXCircle,
  FiMapPin,
  FiPhone,
  FiShoppingBag,
  FiImage,
  FiNavigation,
} from "react-icons/fi";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { useAuth } from "@/contexts/AuthContext";
import { ordersAPI, productsAPI, deliveryAPI } from "@/lib/api";
import { formatCurrency, formatDate, formatTime } from "@/lib/utils";
import toast from "react-hot-toast";
import StaticMap from "@/components/maps/StaticMap";

export default function OrderDetailsPage() {
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const params = useParams();
  const orderId = params.id;

  const [order, setOrder] = useState(null);
  const [products, setProducts] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [hawkerLocation, setHawkerLocation] = useState(null);
  const [refreshInterval, setRefreshInterval] = useState(null);

  // Fetch order data
  useEffect(() => {
    const fetchOrderDetails = async () => {
      try {
        if (!isAuthenticated) {
          setLoading(false);
          return;
        }

        setLoading(true);
        const response = await ordersAPI.getOrderById(orderId);
        
        if (response.data && response.data.status === "success") {
          setOrder(response.data.data);
        } else if (response.data) {
          setOrder(response.data);
        } else {
          setError("Failed to load order details. Unexpected response format.");
        }
      } catch (err) {
        console.error("Error fetching order details:", err);
        setError("Failed to load order details. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchOrderDetails();
  }, [isAuthenticated, orderId]);

  // Fetch product details
  useEffect(() => {
    const fetchProductDetails = async () => {
      if (!order || !order.items || order.items.length === 0) return;
      
      try {
        // Extract all unique product IDs from order
        const productIds = new Set();
        order.items.forEach(item => {
          if (item.product_id) {
            productIds.add(item.product_id);
          }
        });
        
        const uniqueProductIds = Array.from(productIds);
        
        if (uniqueProductIds.length === 0) return;
        
        // For each product ID, fetch details
        const productDetails = {};
        
        const fetchPromises = uniqueProductIds.map(async (productId) => {
          try {
            const response = await productsAPI.getProductById(productId);
            
            if (response.data) {
              productDetails[productId] = response.data;
            }
          } catch (err) {
            console.error(`Error fetching product ${productId}:`, err);
          }
        });
        
        await Promise.all(fetchPromises);
        setProducts(productDetails);
        
      } catch (err) {
        console.error("Error fetching product details:", err);
      }
    };
    
    fetchProductDetails();
  }, [order]);

  // Track hawker location if order is in "delivering" or "assigned" status
  useEffect(() => {
    // Clear any existing interval when component unmounts or order changes
    return () => {
      if (refreshInterval) {
        clearInterval(refreshInterval);
      }
    };
  }, [refreshInterval]);

  // Set up tracking interval when order is loaded
  useEffect(() => {
    if (!order) return;
    
    // Check if order is in a trackable state
    const isTrackable = order.status === "delivering" || order.status === "assigned";
    
    if (isTrackable && order.hawker_id) {
      // Start tracking hawker location
      const trackHawker = async () => {
        try {
          const response = await deliveryAPI.trackHawker(order.hawker_id);
          
          if (response.data && response.data.status === "success") {
            setHawkerLocation(response.data.data);
          } else if (response.data && response.data.latitude && response.data.longitude) {
            setHawkerLocation(response.data);
          } else {
            console.log("No location data available for this hawker");
          }
        } catch (err) {
          console.error("Error tracking hawker:", err);
        }
      };
      
      // Track immediately and then set interval
      trackHawker();
      
      // Set up 30-second refresh interval for tracking
      const interval = setInterval(trackHawker, 30000);
      setRefreshInterval(interval);
      
      return () => clearInterval(interval);
    } else {
      // Clear interval if order is not trackable
      if (refreshInterval) {
        clearInterval(refreshInterval);
        setRefreshInterval(null);
      }
    }
  }, [order, refreshInterval]);

  if (!isAuthenticated) {
    router.push("/login?redirect=/orders");
    return null;
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="h-8 bg-gray-200 rounded w-1/4 animate-pulse"></div>
        <div className="h-48 bg-gray-200 rounded-lg animate-pulse"></div>
        <div className="h-64 bg-gray-200 rounded-lg animate-pulse"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-4">
        <Link href="/orders" className="flex items-center text-gray-600 hover:text-gray-900">
          <FiArrowLeft className="mr-2" /> Back to Orders
        </Link>
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
          {error}
        </div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="space-y-4">
        <Link href="/orders" className="flex items-center text-gray-600 hover:text-gray-900">
          <FiArrowLeft className="mr-2" /> Back to Orders
        </Link>
        <div className="text-center py-12">
          <h2 className="text-xl font-semibold mb-2">Order not found</h2>
          <p className="text-gray-600 mb-4">
            The order you're looking for doesn't exist or you don't have permission to view it.
          </p>
        </div>
      </div>
    );
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case "pending":
        return <FiClock className="text-orange-500" />;
      case "confirmed":
      case "preparing":
        return <FiClock className="text-blue-500" />;
      case "delivering":
      case "assigned":
        return <FiTruck className="text-blue-500" />;
      case "delivered":
        return <FiCheckCircle className="text-green-500" />;
      case "cancelled":
        return <FiXCircle className="text-red-500" />;
      default:
        return <FiClock className="text-gray-500" />;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case "pending":
        return "Pending";
      case "confirmed":
        return "Confirmed";
      case "preparing":
        return "Preparing";
      case "delivering":
        return "Out for Delivery";
      case "assigned":
        return "Assigned to Hawker";
      case "delivered":
        return "Delivered";
      case "cancelled":
        return "Cancelled";
      default:
        return status;
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case "pending":
        return "bg-orange-100 text-orange-800";
      case "confirmed":
      case "preparing":
        return "bg-blue-100 text-blue-800";
      case "delivering":
      case "assigned":
        return "bg-indigo-100 text-indigo-800";
      case "delivered":
        return "bg-green-100 text-green-800";
      case "cancelled":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };
  
  // Get product details including image URL
  const getProductDetails = (productId) => {
    if (products[productId]) {
      return products[productId];
    }
    return null;
  };
  
  // Calculate order subtotal
  const subtotal = order.items.reduce((sum, item) => {
    return sum + (item.price * item.quantity);
  }, 0);
  
  const cancelOrder = async () => {
    try {
      await ordersAPI.cancelOrder(order.id);
      toast.success("Order cancelled successfully", {
        icon: '🚫'
      });
      // Update the order status locally
      setOrder({
        ...order,
        status: "cancelled"
      });
    } catch (err) {
      console.error("Error cancelling order:", err);
      toast.error("Failed to cancel order. Please try again.");
    }
  };

  const isOrderTrackable = (order.status === "delivering" || order.status === "assigned") && !!hawkerLocation;
  
  return (
    <div className="space-y-6">
      <Link href="/orders" className="flex items-center text-gray-600 hover:text-gray-900">
        <FiArrowLeft className="mr-2" /> Back to Orders
      </Link>
      
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center">
        <h1 className="text-2xl font-bold">Order #{order.id}</h1>
        <div className="flex items-center mt-2 sm:mt-0">
          <div className="mr-3">{getStatusIcon(order.status)}</div>
          <span
            className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getStatusClass(
              order.status
            )}`}
          >
            {getStatusText(order.status)}
          </span>
        </div>
      </div>
      
      <Card>
        <div className="flex flex-col sm:flex-row justify-between border-b border-gray-200 pb-4 mb-4">
          <div>
            <h3 className="font-medium text-gray-700">Order Details</h3>
            <p className="text-sm text-gray-500 mt-1">
              Placed on {formatDate(order.created_at)} at {formatTime(order.created_at)}
            </p>
          </div>
          <div className="mt-2 sm:mt-0 text-right">
            <p className="font-bold text-orange-600">
              {formatCurrency(order.total_amount)}
            </p>
            <p className="text-sm text-gray-600">
              {order.payment_status === "paid" ? "Paid" : "Payment Pending"}
            </p>
          </div>
        </div>
        
        <div className="mb-6">
          <h3 className="font-medium mb-3 text-black">Items:</h3>
          <div className="space-y-3">
            {order.items.map((item) => {
              const productDetails = getProductDetails(item.product_id);
              const imageUrl = productDetails?.image_url;
              
              return (
                <div key={item.id} className="flex items-center border-b border-gray-100 pb-3">
                  <div className="w-16 h-16 mr-4 rounded overflow-hidden bg-gray-100 flex items-center justify-center">
                    {imageUrl ? (
                      <div 
                        className="w-full h-full bg-cover bg-center"
                        style={{
                          backgroundImage: `url(${imageUrl})`,
                          backgroundSize: 'contain',
                          backgroundPosition: 'center',
                          backgroundRepeat: 'no-repeat'
                        }}
                      />
                    ) : (
                      <FiImage className="text-gray-400" size={24} />
                    )}
                  </div>
                  <div className="flex-grow">
                    <p className="font-medium text-gray-900">
                      {item.product_name || productDetails?.name || `Product ${item.product_id}`}
                    </p>
                    <div className="flex justify-between mt-1">
                      <p className="text-sm text-gray-600">
                        {formatCurrency(item.price)} x {item.quantity}
                      </p>
                      <p className="text-sm font-medium text-black">
                        {formatCurrency(item.price * item.quantity)}
                      </p>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
          
          {/* Price summary */}
          <div className="mt-4 border-t border-gray-200 pt-4">
            <div className="flex justify-between mb-1">
              <p className="text-gray-600">Subtotal</p>
              <p className="font-medium text-black">{formatCurrency(subtotal)}</p>
            </div>
            <div className="flex justify-between mb-1">
              <p className="text-gray-600">Delivery Fee</p>
              <p className="font-medium text-black">{formatCurrency(order.delivery_fee || 0)}</p>
            </div>
            {order.discount > 0 && (
              <div className="flex justify-between mb-1 text-green-600">
                <p>Discount</p>
                <p className="font-medium">-{formatCurrency(order.discount)}</p>
              </div>
            )}
            <div className="flex justify-between font-bold mt-2 pt-2 border-t border-gray-200 text-black">
              <p>Total</p>
              <p className="text-orange-600">{formatCurrency(order.total_amount)}</p>
            </div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Delivery Information */}
          <div>
            <h3 className="font-medium mb-3 text-black">Delivery Information</h3>
            <div className="bg-gray-50 p-4 rounded">
              <div className="mb-3">
                <h4 className="text-sm font-medium text-gray-700">Address:</h4>
                <p className="text-gray-600">{order.delivery_address}</p>
              </div>
       
              {order.delivery_notes && (
                <div>
                  <h4 className="text-sm font-medium text-gray-700">Notes:</h4>
                  <p className="text-gray-600">{order.delivery_notes}</p>
                </div>
              )}
            </div>
          </div>
          
          {/* Hawker Information */}
          {/* <div>
            <h3 className="font-medium mb-3">Hawker Information</h3>
            <div className="bg-gray-50 p-4 rounded">
              {order.hawker_name ? (
                <>
                  <p className="font-medium">{order.hawker_name}</p>
                  {order.hawker_phone && (
                    <p className="text-sm text-gray-600 mb-2">{order.hawker_phone}</p>
                  )}
                  {isOrderTrackable && (
                    <div className="mt-3">
                      <p className="text-sm text-green-600 mb-2">
                        <FiTruck className="inline mr-1" /> Your hawker is on the way!
                      </p>
                    </div>
                  )}
                </>
              ) : (
                <p className="text-gray-600">Hawker information not available</p>
              )}
            </div>
          </div> */}
        </div>
        
        {/* Live tracking map */}
        {isOrderTrackable && (
          <div className="mt-6">
            <h3 className="font-medium mb-3">Live Tracking</h3>
            <div className="bg-gray-50 p-4 rounded">
              <StaticMap
                latitude={hawkerLocation.latitude}
                longitude={hawkerLocation.longitude}
                title={`${order.hawker_name || 'Hawker'} - Live Location`}
                className="h-64 w-full mb-3"
              />
              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-600">
                  <FiMapPin className="inline mr-1" /> Hawker's current location
                </p>
                <Link 
                  href={`https://www.google.com/maps?q=${hawkerLocation.latitude},${hawkerLocation.longitude}`}
                  target="_blank"
                  className="text-xs text-orange-500 hover:underline"
                >
                  Open in Google Maps
                </Link>
              </div>
              <p className="text-xs text-gray-500 mt-2">
                Location updates every 30 seconds. Last updated: {formatTime(new Date())}
              </p>
            </div>
          </div>
        )}
        
        {/* Actions */}
        <div className="mt-6 flex flex-wrap gap-3 justify-end">
          {(order.status === "pending" || order.status === "confirmed") && (
            <Button 
              variant="outline" 
              className="text-red-600 border-red-600 hover:bg-red-50"
              onClick={cancelOrder}
            >
              Cancel Order
            </Button>
          )}
          
          <Link href={`/hawkers/${order.hawker_id}`} passHref>
            <Button variant="outline">View Hawker</Button>
          </Link>
          
          <Button onClick={() => window.print()}>Print Order</Button>
        </div>
      </Card>
    </div>
  );
}
