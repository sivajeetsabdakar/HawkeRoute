"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import {
  FiClock,
  FiCheckCircle,
  FiTruck,
  FiXCircle,
  FiFilter,
  FiImage,
} from "react-icons/fi";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { useAuth } from "@/contexts/AuthContext";
import { ordersAPI, productsAPI } from "@/lib/api";
import { formatCurrency, formatDate, formatTime } from "@/lib/utils";
import toast from "react-hot-toast";
import { useRouter } from "next/navigation";

export default function OrdersPage() {
  const { isAuthenticated, user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [products, setProducts] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const router = useRouter();

  // Fetch orders data
  useEffect(() => {
    const fetchOrders = async () => {
      try {
        if (!isAuthenticated) {
          setLoading(false);
          return;
        }

        setLoading(true);
        const response = await ordersAPI.getOrders();
        
        // Handle different API response formats
        if (response.data && Array.isArray(response.data)) {
          setOrders(response.data);
        } else if (response.data && response.data.status === "success" && Array.isArray(response.data.data)) {
          setOrders(response.data.data);
        } else {
          console.error("Unexpected API response format:", response);
          setOrders([]);
          setError("Received an unexpected response format from the server.");
        }
      } catch (err) {
        console.error("Error fetching orders:", err);
        setError("Failed to load orders. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, [isAuthenticated]);

  // Fetch product details for all product IDs in orders
  useEffect(() => {
    const fetchProductDetails = async () => {
      if (orders.length === 0) return;
      
      try {
        // Extract all unique product IDs from orders
        const productIds = new Set();
        orders.forEach(order => {
          order.items.forEach(item => {
            if (item.product_id) {
              productIds.add(item.product_id);
            }
          });
        });
        
        // Convert Set to Array
        const uniqueProductIds = Array.from(productIds);
        
        if (uniqueProductIds.length === 0) return;
        
        console.log("Fetching details for products:", uniqueProductIds);
        
        // For each product ID, fetch details
        const productDetails = {};
        
        // We'll fetch products one by one since the batch API may not exist
        const fetchPromises = uniqueProductIds.map(async (productId) => {
          try {
            const response = await productsAPI.getProductById(productId);
            
            if (response.data) {
              productDetails[productId] = response.data;
            }
          } catch (err) {
            console.error(`Error fetching product ${productId}:`, err);
            // Still continue with other products
          }
        });
        
        // Wait for all fetch operations to complete
        await Promise.all(fetchPromises);
        
        console.log("Fetched product details:", productDetails);
        setProducts(productDetails);
        
      } catch (err) {
        console.error("Error fetching product details:", err);
      }
    };
    
    fetchProductDetails();
  }, [orders]);

  if (!isAuthenticated) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold mb-4">
          You need to login to view your orders
        </h1>
        <Link href="/login?redirect=/orders">
          <Button>Login</Button>
        </Link>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div className="h-8 bg-gray-200 rounded w-1/4 animate-pulse"></div>
          <div className="h-10 bg-gray-200 rounded w-1/3 animate-pulse"></div>
        </div>

        {[...Array(3)].map((_, index) => (
          <div
            key={index}
            className="h-48 bg-gray-200 rounded-lg animate-pulse"
          ></div>
        ))}
      </div>
    );
  }

  // Determine filter options from available orders
  const statuses = ["all", ...new Set(orders.map((order) => order.status))];

  // Apply filtering
  const filteredOrders =
    statusFilter === "all"
      ? orders
      : orders.filter((order) => order.status === statusFilter);

  // Sort orders by created_at (newest first)
  const sortedOrders = [...filteredOrders].sort(
    (a, b) => new Date(b.created_at) - new Date(a.created_at)
  );
  
  console.log("Sorted orders:", sortedOrders);

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
  


  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <h1 className="text-3xl font-bold">My Orders</h1>

        <div className="relative">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="appearance-none pl-10 pr-8 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500 bg-white"
          >
            {statuses.map((status) => (
              <option key={status} value={status}>
                {status === "all"
                  ? "All Orders"
                  : `${getStatusText(status)} Orders`}
              </option>
            ))}
          </select>
          <FiFilter className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {sortedOrders.length === 0 ? (
        <div className="text-center py-12">
          <h2 className="text-xl font-semibold mb-2">No orders found</h2>
          {statusFilter !== "all" ? (
            <p className="text-gray-600 mb-4">
              You don't have any {getStatusText(statusFilter).toLowerCase()}{" "}
              orders.
            </p>
          ) : (
            <p className="text-gray-600 mb-4">
              You haven't placed any orders yet.
            </p>
          )}
          <Link href="/hawkers">
            <Button>Browse Hawkers</Button>
          </Link>
        </div>
      ) : (
        <div className="space-y-6">
          {sortedOrders.map((order) => (
            <Card key={order.id} className="hover:shadow-md transition-shadow">
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-4 border-b border-gray-200 pb-4 mb-4">
                <div className="flex items-center">
                  <div className="mr-3">{getStatusIcon(order.status)}</div>
                  <div>
                    <span
                      className={`inline-block px-3 py-1 rounded-full text-xs font-medium ${getStatusClass(
                        order.status
                      )}`}
                    >
                      {getStatusText(order.status)}
                    </span>
                    <p className="text-sm text-gray-500 mt-1">
                      {formatDate(order.created_at)} at{" "}
                      {formatTime(order.created_at)}
                    </p>
                  </div>
                </div>
                <div className="sm:ml-auto text-right">
                  <p className="text-sm text-gray-600">Order #{order.id}</p>
                  <p className="font-bold text-orange-600">
                    {formatCurrency(order.total_amount)}
                  </p>
                </div>
              </div>

              <div className="mb-4">
                <h3 className="font-medium mb-2 text-black">Order Items:</h3>
                <div className="grid grid-cols-1 gap-4">
                  {order.items.map((item) => {
                    const productDetails = getProductDetails(item.product_id);
                    const imageUrl = productDetails?.image_url;
                    
                    return (
                      <div key={item.id} className="flex items-center border-b border-gray-100 pb-2">
                        <div className="w-12 h-12 mr-3 rounded overflow-hidden bg-gray-100 flex items-center justify-center">
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
                          <div className="flex justify-between">
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
              </div>
              
              <div className="border-t border-gray-200 pt-4">
                <div className="flex flex-col sm:flex-row justify-between">
                  <div>
                    <h3 className="font-medium mb-1 text-black">Delivery Address:</h3>
                    <p className="text-gray-600 text-sm mb-2">{order.delivery_address}</p>
                    {order.hawker_name && (
                      <div className="text-sm text-gray-600">
                        <span className="font-medium">Hawker:</span> {order.hawker_name}
                      </div>
                    )}
                  </div>
                  
                  <div className="flex mt-4 sm:mt-0 gap-2">
                    {(order.status === "pending" || order.status === "confirmed") && (
                      <Button 
                        size="sm" 
                        variant="outline"
                        className="text-red-600 border-red-600 hover:bg-red-50"
                        onClick={() => cancelOrder(order.id)}
                      >
                        Cancel Order
                      </Button>
                    )}
                    
                    <Link href={`/orders/${order.id}`}>
                      <Button size="sm" variant="outline">
                        View Details
                      </Button>
                    </Link>

                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
