"use client";

import { useState, useEffect } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import {
  FiArrowLeft,
  FiCheck,
  FiCreditCard,
  FiDollarSign,
  FiClock,
} from "react-icons/fi";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { ordersAPI, paymentsAPI } from "@/lib/api";
import { formatCurrency, formatDate } from "@/lib/utils";

export default function PaymentPage() {
  const router = useRouter();
  const { orderId } = useParams();

  const [order, setOrder] = useState(null);
  const [loading, setLoading] = useState(true);
  const [paymentLoading, setPaymentLoading] = useState(false);
  const [error, setError] = useState("");
  const [paymentMethod, setPaymentMethod] = useState("card");
  const [paymentStatus, setPaymentStatus] = useState("pending"); // pending, processing, success, failed

  useEffect(() => {
    const fetchOrderDetails = async () => {
      try {
        setLoading(true);
        const response = await ordersAPI.getOrderById(orderId);
        setOrder(response.data);
      } catch (err) {
        console.error("Error fetching order:", err);
        setError("Failed to load order details. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchOrderDetails();
  }, [orderId]);

  const handlePayment = async () => {
    try {
      setPaymentLoading(true);
      setError("");
      setPaymentStatus("processing");

      if (paymentMethod === "card") {
        // Initialize payment with payment gateway
        const initResponse = await paymentsAPI.initiatePayment(orderId);

        // In a real app, this would open the payment gateway UI
        // For now, simulate a successful payment after a delay
        setTimeout(async () => {
          try {
            // Mock payment verification
            const verifyData = {
              razorpay_payment_id:
                "pay_" + Math.random().toString(36).substr(2, 9),
              razorpay_order_id: initResponse.data.order_id,
              razorpay_signature: "signature",
            };

            const verifyResponse = await paymentsAPI.verifyPayment(verifyData);

            setPaymentStatus("success");
            setTimeout(() => {
              router.push(`/orders/${orderId}`);
            }, 2000);
          } catch (err) {
            console.error("Payment verification failed:", err);
            setError("Payment verification failed. Please try again.");
            setPaymentStatus("failed");
          } finally {
            setPaymentLoading(false);
          }
        }, 2000);
      } else if (paymentMethod === "cod") {
        // Record Cash on Delivery payment
        await paymentsAPI.recordCODPayment(orderId);

        setPaymentStatus("success");
        setTimeout(() => {
          router.push(`/orders/${orderId}`);
        }, 2000);
        setPaymentLoading(false);
      }
    } catch (err) {
      console.error("Payment failed:", err);
      setError("Payment processing failed. Please try again.");
      setPaymentStatus("failed");
      setPaymentLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="space-y-8 animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/3"></div>
        <div className="h-64 bg-gray-200 rounded-lg"></div>
      </div>
    );
  }

  if (error && !order) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
        {error}
        <div className="mt-4">
          <Link href="/orders">
            <Button>View My Orders</Button>
          </Link>
        </div>
      </div>
    );
  }

  if (!order) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-800">Order not found</h2>
        <p className="text-gray-600 mt-2">
          The order you're looking for doesn't exist.
        </p>
        <Link href="/orders">
          <Button className="mt-6">View My Orders</Button>
        </Link>
      </div>
    );
  }

  // Render different content based on payment status
  const renderPaymentStatus = () => {
    switch (paymentStatus) {
      case "processing":
        return (
          <div className="text-center py-8">
            <FiClock size={64} className="mx-auto text-orange-600 mb-4" />
            <h2 className="text-2xl font-bold mb-2">Processing Payment</h2>
            <p className="text-gray-600 mb-6">
              Please wait while we process your payment...
            </p>
            <div className="w-16 h-16 border-4 border-orange-200 border-t-orange-600 rounded-full animate-spin mx-auto"></div>
          </div>
        );
      case "success":
        return (
          <div className="text-center py-8">
            <div className="w-16 h-16 rounded-full bg-green-100 flex items-center justify-center mx-auto mb-4">
              <FiCheck size={32} className="text-green-600" />
            </div>
            <h2 className="text-2xl font-bold mb-2">Payment Successful!</h2>
            <p className="text-gray-600 mb-6">Your order has been confirmed.</p>
            <p className="text-gray-600">Redirecting to order details...</p>
          </div>
        );
      case "failed":
        return (
          <div className="text-center py-8">
            <div className="w-16 h-16 rounded-full bg-red-100 flex items-center justify-center mx-auto mb-4">
              <span className="text-red-600 text-2xl font-bold">✕</span>
            </div>
            <h2 className="text-2xl font-bold mb-2">Payment Failed</h2>
            <p className="text-red-600 mb-6">
              {error || "An error occurred during payment processing."}
            </p>
            <Button onClick={() => setPaymentStatus("pending")}>
              Try Again
            </Button>
          </div>
        );
      default: // pending
        return (
          <>
            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-2">
                Select Payment Method
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div
                  className={`border rounded-lg p-4 cursor-pointer ${
                    paymentMethod === "card"
                      ? "border-orange-600 bg-orange-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                  onClick={() => setPaymentMethod("card")}
                >
                  <div className="flex items-center">
                    <FiCreditCard
                      size={24}
                      className={
                        paymentMethod === "card"
                          ? "text-orange-600"
                          : "text-gray-400"
                      }
                    />
                    <span className="ml-2 font-medium">Credit/Debit Card</span>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">
                    Pay securely with your card
                  </p>
                </div>
                <div
                  className={`border rounded-lg p-4 cursor-pointer ${
                    paymentMethod === "cod"
                      ? "border-orange-600 bg-orange-50"
                      : "border-gray-200 hover:border-gray-300"
                  }`}
                  onClick={() => setPaymentMethod("cod")}
                >
                  <div className="flex items-center">
                    <FiDollarSign
                      size={24}
                      className={
                        paymentMethod === "cod"
                          ? "text-orange-600"
                          : "text-gray-400"
                      }
                    />
                    <span className="ml-2 font-medium">Cash on Delivery</span>
                  </div>
                  <p className="text-sm text-gray-500 mt-1">
                    Pay when you receive your food
                  </p>
                </div>
              </div>
            </div>

            <Button
              fullWidth
              onClick={handlePayment}
              isLoading={paymentLoading}
            >
              {paymentMethod === "card" ? "Pay Now" : "Confirm Order"}
            </Button>
          </>
        );
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="flex items-center mb-8">
        <button
          onClick={() => router.back()}
          className="mr-4 text-gray-600 hover:text-gray-900 flex items-center"
        >
          <FiArrowLeft className="mr-1" />
          <span>Back</span>
        </button>
        <h1 className="text-3xl font-bold">Payment</h1>
      </div>

      <div className="grid grid-cols-1 gap-8">
        <Card>
          <h2 className="text-xl font-semibold mb-4">Order Summary</h2>
          <div className="mb-4">
            <div className="flex justify-between py-2">
              <span className="text-gray-600">Order ID</span>
              <span className="font-medium">{order.id}</span>
            </div>
            <div className="flex justify-between py-2">
              <span className="text-gray-600">Date</span>
              <span className="font-medium">
                {formatDate(order.created_at)}
              </span>
            </div>
            <div className="flex justify-between py-2 border-t border-gray-200">
              <span className="text-gray-600">Items Total</span>
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

          <div className="border-t border-gray-200 pt-4">
            <h3 className="font-semibold mb-2">Delivery Address</h3>
            <p className="text-gray-600">{order.delivery_address}</p>

            {order.delivery_instructions && (
              <>
                <h3 className="font-semibold mt-4 mb-2">
                  Delivery Instructions
                </h3>
                <p className="text-gray-600">{order.delivery_instructions}</p>
              </>
            )}
          </div>
        </Card>

        <Card>{renderPaymentStatus()}</Card>
      </div>
    </div>
  );
}
