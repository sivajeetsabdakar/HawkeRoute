"use client";

import { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  FiArrowLeft,
  FiShoppingCart,
  FiTrash2,
  FiMinus,
  FiPlus,
  FiImage,
} from "react-icons/fi";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { useCart } from "@/contexts/CartContext";
import { useAuth } from "@/contexts/AuthContext";
import { formatCurrency } from "@/lib/utils";
import { ordersAPI } from "@/lib/api";
import { getCurrentPosition } from "@/lib/location";

export default function CartPage() {
  const router = useRouter();
  const {
    cart,
    updateItemQuantity,
    removeFromCart,
    clearCart,
    getTotalAmount,
    isEmpty,
    hawkerId,
  } = useCart();
  const { user, isAuthenticated } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [deliveryAddress, setDeliveryAddress] = useState("");
  const [deliveryInstructions, setDeliveryInstructions] = useState("");

  const handleQuantityChange = (productId, newQuantity) => {
    updateItemQuantity(productId, newQuantity);
  };

  const handleRemoveItem = (productId) => {
    removeFromCart(productId);
  };

  const handleClearCart = () => {
    if (window.confirm("Are you sure you want to clear your cart?")) {
      clearCart();
    }
  };

  const handleCheckout = async () => {
    try {
      if (!isAuthenticated) {
        router.push("/login?redirect=/cart");
        return;
      }

      if (!deliveryAddress.trim()) {
        setError("Please enter a delivery address");
        return;
      }

      setLoading(true);
      setError("");

      // Get current position for delivery coordinates
      const position = await getCurrentPosition();

      // Create order data
      const orderData = {
        hawker_id: hawkerId,
        items: cart.items.map((item) => ({
          product_id: item.product_id,
          quantity: item.quantity,
        })),
        delivery_address: deliveryAddress,
        delivery_latitude: position.latitude,
        delivery_longitude: position.longitude,
        delivery_instructions: deliveryInstructions,
      };

      // Create order
      const response = await ordersAPI.createOrder(orderData);

      // Clear cart
      clearCart();

      // Redirect to payment page
      router.push(`/payment/${response.data.id}`);
    } catch (err) {
      console.error("Error creating order:", err);
      setError("Failed to create order. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  if (isEmpty) {
    return (
      <div className="flex flex-col items-center justify-center py-12">
        <div className="text-center">
          <FiShoppingCart size={64} className="mx-auto text-gray-400 mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Your cart is empty
          </h1>
          <p className="text-gray-600 mb-8">
            Looks like you haven't added any items to your cart yet.
          </p>
          <Link href="/hawkers">
            <Button>Browse Hawkers</Button>
          </Link>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex items-center mb-8">
        <button
          onClick={() => router.back()}
          className="mr-4 text-gray-600 hover:text-gray-900 flex items-center"
        >
          <FiArrowLeft className="mr-1" />
          <span>Back</span>
        </button>
        <h1 className="text-3xl font-bold">Your Cart</h1>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          <Card>
            <div className="space-y-4">
              {cart.items.map((item) => (
                <div
                  key={item.product_id}
                  className="flex items-center border-b border-gray-200 pb-4 last:border-0"
                >
                  <div className="relative w-20 h-20 mr-4 rounded-md overflow-hidden bg-gray-100">
                    <div
                      className="w-full h-full bg-cover bg-center"
                      style={{
                        backgroundImage: `url('/images/product-default.jpg')`,
                        backgroundSize: "cover",
                        backgroundPosition: "center",
                      }}
                    >
                      <div className="flex items-center justify-center h-full">
                        <FiImage size={16} className="text-gray-400" />
                      </div>
                    </div>
                  </div>
                  <div className="flex-grow">
                    <h3 className="font-medium text-gray-900">{item.name}</h3>
                    <p className="text-gray-600 text-sm">
                      {formatCurrency(item.price)} x {item.quantity}
                    </p>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() =>
                        handleQuantityChange(item.product_id, item.quantity - 1)
                      }
                      className="p-1 text-gray-500 hover:text-gray-700"
                      aria-label="Decrease quantity"
                    >
                      <FiMinus size={16} />
                    </button>
                    <span className="w-8 text-center">{item.quantity}</span>
                    <button
                      onClick={() =>
                        handleQuantityChange(item.product_id, item.quantity + 1)
                      }
                      className="p-1 text-gray-500 hover:text-gray-700"
                      aria-label="Increase quantity"
                    >
                      <FiPlus size={16} />
                    </button>
                    <button
                      onClick={() => handleRemoveItem(item.product_id)}
                      className="p-1 text-red-500 hover:text-red-700 ml-2"
                      aria-label="Remove item"
                    >
                      <FiTrash2 size={18} />
                    </button>
                  </div>
                </div>
              ))}
            </div>

            <div className="mt-4 flex justify-end">
              <Button
                variant="outline"
                className="text-red-600 border-red-600 hover:bg-red-50"
                onClick={handleClearCart}
              >
                Clear Cart
              </Button>
            </div>
          </Card>
        </div>

        <div className="lg:col-span-1">
          <Card title="Order Summary">
            <div className="space-y-4">
              <div className="flex justify-between">
                <span className="text-gray-600">Subtotal</span>
                <span className="font-medium">
                  {formatCurrency(getTotalAmount())}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-gray-600">Delivery Fee</span>
                <span className="font-medium">{formatCurrency(5)}</span>
              </div>
              <div className="border-t border-gray-200 pt-4 flex justify-between">
                <span className="font-semibold">Total</span>
                <span className="font-bold text-orange-600">
                  {formatCurrency(getTotalAmount() + 5)}
                </span>
              </div>
            </div>

            <div className="mt-6 space-y-4">
              <div>
                <label
                  htmlFor="address"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Delivery Address <span className="text-red-500">*</span>
                </label>
                <textarea
                  id="address"
                  rows={3}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500"
                  placeholder="Enter your full delivery address"
                  value={deliveryAddress}
                  onChange={(e) => setDeliveryAddress(e.target.value)}
                  required
                ></textarea>
              </div>

              <div>
                <label
                  htmlFor="instructions"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Delivery Instructions (optional)
                </label>
                <textarea
                  id="instructions"
                  rows={2}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500"
                  placeholder="Any specific instructions for delivery"
                  value={deliveryInstructions}
                  onChange={(e) => setDeliveryInstructions(e.target.value)}
                ></textarea>
              </div>

              <Button fullWidth isLoading={loading} onClick={handleCheckout}>
                Proceed to Checkout
              </Button>

              {!isAuthenticated && (
                <p className="text-sm text-red-600">
                  You need to{" "}
                  <Link href="/login?redirect=/cart" className="underline">
                    login
                  </Link>{" "}
                  to complete your order.
                </p>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
