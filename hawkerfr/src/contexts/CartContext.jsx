"use client";

import { createContext, useContext, useEffect, useState } from "react";

const CartContext = createContext(null);

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState({ items: [], hawker_id: null });
  const [loading, setLoading] = useState(true);

  // Load cart from localStorage on component mount
  useEffect(() => {
    const savedCart = localStorage.getItem("cart");
    if (savedCart) {
      try {
        setCart(JSON.parse(savedCart));
      } catch (error) {
        console.error("Error parsing cart from localStorage:", error);
      }
    }
    setLoading(false);
  }, []);

  // Save cart to localStorage whenever it changes
  useEffect(() => {
    if (!loading) {
      localStorage.setItem("cart", JSON.stringify(cart));
    }
  }, [cart, loading]);

  // Add item to cart
  const addToCart = (product, quantity = 1) => {
    setCart((prevCart) => {
      // If the cart is empty or from a different hawker, start a new cart
      if (
        prevCart.hawker_id !== null &&
        prevCart.hawker_id !== product.hawker_id
      ) {
        if (
          !window.confirm(
            "This will clear your current cart as you can only order from one hawker at a time. Continue?"
          )
        ) {
          return prevCart;
        }
      }

      // Check if the item is already in the cart
      const existingItemIndex = prevCart.items.findIndex(
        (item) => item.product_id === product.id
      );

      if (existingItemIndex !== -1) {
        // Update quantity if item exists
        const updatedItems = [...prevCart.items];
        updatedItems[existingItemIndex] = {
          ...updatedItems[existingItemIndex],
          quantity: updatedItems[existingItemIndex].quantity + quantity,
        };

        return {
          ...prevCart,
          items: updatedItems,
        };
      } else {
        // Add new item if it doesn't exist
        return {
          items: [
            ...prevCart.items,
            {
              product_id: product.id,
              name: product.name,
              price: product.price,
              image_url: product.image_url,
              quantity,
            },
          ],
          hawker_id: product.hawker_id,
        };
      }
    });
  };

  // Update item quantity
  const updateItemQuantity = (productId, quantity) => {
    setCart((prevCart) => {
      if (quantity <= 0) {
        // Remove item if quantity is 0 or negative
        return {
          ...prevCart,
          items: prevCart.items.filter((item) => item.product_id !== productId),
        };
      } else {
        // Update quantity
        return {
          ...prevCart,
          items: prevCart.items.map((item) =>
            item.product_id === productId ? { ...item, quantity } : item
          ),
        };
      }
    });
  };

  // Remove item from cart
  const removeFromCart = (productId) => {
    setCart((prevCart) => ({
      ...prevCart,
      items: prevCart.items.filter((item) => item.product_id !== productId),
    }));
  };

  // Clear cart
  const clearCart = () => {
    setCart({ items: [], hawker_id: null });
  };

  // Calculate total amount
  const getTotalAmount = () => {
    return cart.items.reduce(
      (total, item) => total + item.price * item.quantity,
      0
    );
  };

  // Calculate total quantity
  const getTotalQuantity = () => {
    return cart.items.reduce((total, item) => total + item.quantity, 0);
  };

  const value = {
    cart,
    loading,
    addToCart,
    updateItemQuantity,
    removeFromCart,
    clearCart,
    getTotalAmount,
    getTotalQuantity,
    isEmpty: cart.items.length === 0,
    hawkerId: cart.hawker_id,
  };

  return <CartContext.Provider value={value}>{children}</CartContext.Provider>;
};

// Custom hook to use the cart context
export const useCart = () => {
  const context = useContext(CartContext);
  if (context === null) {
    throw new Error("useCart must be used within a CartProvider");
  }
  return context;
};

export default CartContext;
