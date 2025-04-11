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
} from "react-icons/fi";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { useAuth } from "@/contexts/AuthContext";
import { ordersAPI, deliveryAPI } from "@/lib/api";
import { formatCurrency, formatDate, formatTime } from "@/lib/utils";
import {
  joinTrackingRoom,
  onLocationUpdate,
  leaveTrackingRoom,
} from "@/lib/socket";

export default function OrderDetailPage() {
  const { id } = useParams();
  const router = useRouter();
  const { isAuthenticated } = useAuth();

  const [order, setOrder] = useState(null);
  const [hawker, setHawker] = useState(null);
  const [tracking, setTracking] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [hawkerLocation, setHawkerLocation] = useState(null);

  useEffect(() => {
    const fetchOrderDetails = async () => {
      try {
        if (!isAuthenticated) {
          setLoading(false);
          return;
        }

        setLoading(true);
        const response = await ordersAPI.getOrderById(id);
        setOrder(response.data);

        // If order is in delivery state, get tracking info
        if (response.data.status === "delivering") {
          try {
            const trackingResponse = await deliveryAPI.trackHawker(
              response.data.hawker_id
            );
            setTracking(trackingResponse.data);
            setHawker(trackingResponse.data.hawker);

            // Join the tracking room to get real-time updates
            joinTrackingRoom(response.data.hawker_id);
          } catch (trackingErr) {
            console.error("Error fetching tracking info:", trackingErr);
          }
        }
      } catch (err) {
        console.error("Error fetching order:", err);
        setError("Failed to load order details. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchOrderDetails();

    // Set up real-time location updates
    const unsubscribe = onLocationUpdate((data) => {
      if (data && data.hawker_id === order?.hawker_id) {
        setHawkerLocation({
          latitude: data.latitude,
          longitude: data.longitude,
          timestamp: data.timestamp,
        });
      }
    });

    // Clean up
    return () => {
      if (order?.hawker_id) {
        leaveTrackingRoom(order.hawker_id);
      }
      unsubscribe();
    };
  }, [id, isAuthenticated, order?.hawker_id]);

  if (!isAuthenticated) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold mb-4">
          You need to login to view order details
        </h1>
        <Link href={`/login?redirect=/orders/${id}`}>
          <Button>Login</Button>
        </Link>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="space-y-6 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/4"></div>
        <div className="h-64 bg-gray-200 rounded-lg"></div>
        <div className="h-64 bg-gray-200 rounded-lg"></div>
      </div>
    );
  }

  if (error || !order) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
        {error || "Order not found"}
        <div className="mt-4">
          <Link href="/orders">
            <Button>Back to Orders</Button>
          </Link>
        </div>
      </div>
    );
  }

  const getStatusIcon = (status) => {
    switch (status) {
      case "pending":
        return <FiClock size={24} className="text-orange-500" />;
      case "confirmed":
      case "preparing":
        return <FiClock size={24} className="text-blue-500" />;
      case "delivering":
        return <FiTruck size={24} className="text-blue-500" />;
      case "delivered":
        return <FiCheckCircle size={24} className="text-green-500" />;
      case "cancelled":
        return <FiXCircle size={24} className="text-red-500" />;
      default:
        return <FiClock size={24} className="text-gray-500" />;
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
        return "bg-indigo-100 text-indigo-800";
      case "delivered":
        return "bg-green-100 text-green-800";
      case "cancelled":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center mb-8">
        <button
          onClick={() => router.back()}
          className="mr-4 text-gray-600 hover:text-gray-900 flex items-center"
        >
          <FiArrowLeft className="mr-1" />
          <span>Back</span>
        </button>
        <h1 className="text-3xl font-bold">Order Details</h1>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-2 space-y-6">
          {/* Order Status */}
          <Card>
            <div className="flex items-center mb-6">
              {getStatusIcon(order.status)}
              <div className="ml-4">
                <h2 className="text-xl font-semibold">
                  {getStatusText(order.status)}
                </h2>
                <p className="text-gray-600">
                  Order #{order.id} • {formatDate(order.created_at)} at{" "}
                  {formatTime(order.created_at)}
                </p>
              </div>
              <span
                className={`ml-auto px-3 py-1 rounded-full text-xs font-medium ${getStatusClass(
                  order.status
                )}`}
              >
                {getStatusText(order.status)}
              </span>
            </div>

            {/* Delivery Tracking (only for delivering orders) */}
            {order.status === "delivering" && tracking && (
              <div className="border-t border-gray-200 pt-4">
                <h3 className="font-semibold mb-3">Delivery Tracking</h3>
                <div className="bg-blue-50 rounded-lg p-4">
                  <div className="flex items-center mb-2">
                    <FiTruck className="text-blue-600 mr-2" />
                    <span className="font-medium">
                      Your order is on the way!
                    </span>
                  </div>
                  <p className="text-sm text-gray-600 mb-2">
                    Estimated delivery time: 15-25 minutes
                  </p>
                  <div className="flex items-center text-sm text-gray-600">
                    <FiMapPin className="mr-1" />
                    <span>
                      Last updated:{" "}
                      {hawkerLocation
                        ? formatTime(hawkerLocation.timestamp)
                        : "No updates yet"}
                    </span>
                  </div>
                </div>
              </div>
            )}
          </Card>

          {/* Order Items */}
          <Card title="Order Items">
            <div className="space-y-4">
              {order.items.map((item) => (
                <div
                  key={item.id}
                  className="flex items-center border-b border-gray-200 pb-4 last:border-0"
                >
                  <div className="relative w-16 h-16 mr-4 rounded-md overflow-hidden">
                    <Image
                      src={item.image_url || "/images/product-default.jpg"}
                      alt={item.name || `Product ${item.product_id}`}
                      fill
                      className="object-cover"
                    />
                  </div>
                  <div className="flex-grow">
                    <h3 className="font-medium text-gray-900">
                      {item.name || `Product ${item.product_id}`}
                    </h3>
                    <p className="text-gray-600 text-sm">
                      {formatCurrency(item.price)} x {item.quantity}
                    </p>
                  </div>
                  <div className="text-right">
                    <p className="font-semibold text-gray-900">
                      {formatCurrency(item.price * item.quantity)}
                    </p>
                  </div>
                </div>
              ))}

              <div className="pt-4">
                <div className="flex justify-between py-2">
                  <span className="text-gray-600">Subtotal</span>
                  <span className="font-medium">
                    {formatCurrency(order.total_amount - 5)}
                  </span>
                </div>
                <div className="flex justify-between py-2">
                  <span className="text-gray-600">Delivery Fee</span>
                  <span className="font-medium">{formatCurrency(5)}</span>
                </div>
                <div className="flex justify-between py-2 border-t border-gray-200 font-bold">
                  <span>Total</span>
                  <span className="text-orange-600">
                    {formatCurrency(order.total_amount)}
                  </span>
                </div>
              </div>
            </div>
          </Card>

          {/* Delivery Information */}
          <Card title="Delivery Information">
            <div className="space-y-4">
              <div className="flex items-start">
                <FiMapPin className="mt-1 mr-3 text-gray-400" />
                <div>
                  <h3 className="font-medium">Delivery Address</h3>
                  <p className="text-gray-600">{order.delivery_address}</p>
                </div>
              </div>

              {order.delivery_instructions && (
                <div className="flex items-start">
                  <FiShoppingBag className="mt-1 mr-3 text-gray-400" />
                  <div>
                    <h3 className="font-medium">Delivery Instructions</h3>
                    <p className="text-gray-600">
                      {order.delivery_instructions}
                    </p>
                  </div>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Hawker Information */}
          <Card title="Hawker Information">
            <div className="space-y-4">
              <div className="flex items-center">
                <div className="relative w-12 h-12 mr-3 rounded-full overflow-hidden">
                  <Image
                    src="/images/hawker-detail.jpg"
                    alt="Hawker"
                    fill
                    className="object-cover"
                  />
                </div>
                <div>
                  <h3 className="font-medium">
                    {hawker?.name || `Hawker ${order.hawker_id}`}
                  </h3>
                  <p className="text-sm text-gray-600">
                    ID: #{order.hawker_id}
                  </p>
                </div>
              </div>

              <div className="flex items-start">
                <FiPhone className="mt-1 mr-3 text-gray-400" />
                <div>
                  <h3 className="font-medium">Contact</h3>
                  <p className="text-gray-600">+1234567890</p>
                </div>
              </div>
            </div>

            <div className="mt-4 pt-4 border-t border-gray-200">
              <Link href={`/hawkers/${order.hawker_id}`}>
                <Button variant="outline" fullWidth>
                  Visit Hawker Page
                </Button>
              </Link>
            </div>
          </Card>

          {/* Actions */}
          <Card title="Actions">
            {order.status === "pending" || order.status === "confirmed" ? (
              <Button
                variant="outline"
                className="text-red-600 border-red-600 hover:bg-red-50 w-full mb-2"
              >
                Cancel Order
              </Button>
            ) : null}

            <Link href={`/orders/${id}/support`}>
              <Button variant="outline" fullWidth>
                Contact Support
              </Button>
            </Link>
          </Card>
        </div>
      </div>
    </div>
  );
}
