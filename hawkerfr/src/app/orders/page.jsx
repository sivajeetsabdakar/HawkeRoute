"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import {
  FiClock,
  FiCheckCircle,
  FiTruck,
  FiXCircle,
  FiFilter,
} from "react-icons/fi";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { useAuth } from "@/contexts/AuthContext";
import { ordersAPI } from "@/lib/api";
import { formatCurrency, formatDate, formatTime } from "@/lib/utils";

export default function OrdersPage() {
  const { isAuthenticated, user } = useAuth();
  const [orders, setOrders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");

  useEffect(() => {
    const fetchOrders = async () => {
      try {
        if (!isAuthenticated) {
          setLoading(false);
          return;
        }

        setLoading(true);
        const response = await ordersAPI.getOrders();
        setOrders(response.data);
      } catch (err) {
        console.error("Error fetching orders:", err);
        setError("Failed to load orders. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchOrders();
  }, [isAuthenticated]);

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

  const getStatusIcon = (status) => {
    switch (status) {
      case "pending":
        return <FiClock className="text-orange-500" />;
      case "confirmed":
      case "preparing":
        return <FiClock className="text-blue-500" />;
      case "delivering":
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
                <h3 className="font-medium mb-2">Order Items:</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {order.items.map((item) => (
                    <div key={item.id} className="flex items-center">
                      <div className="relative w-12 h-12 mr-3 rounded overflow-hidden">
                        <Image
                          src={item.image_url || "/images/product-default.jpg"}
                          alt={item.name || `Product ${item.product_id}`}
                          fill
                          className="object-cover"
                        />
                      </div>
                      <div className="flex-grow">
                        <p className="font-medium text-gray-900 text-sm">
                          {item.name || `Product ${item.product_id}`}
                        </p>
                        <p className="text-sm text-gray-600">
                          {formatCurrency(item.price)} x {item.quantity}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              <div className="flex justify-between items-center">
                <div>
                  <p className="text-sm text-gray-600">Delivery to:</p>
                  <p className="text-gray-900">{order.delivery_address}</p>
                </div>
                <Link href={`/orders/${order.id}`}>
                  <Button variant="outline" size="sm">
                    View Details
                  </Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
