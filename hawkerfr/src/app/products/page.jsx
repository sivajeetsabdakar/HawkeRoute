"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import { FiShoppingCart, FiSearch, FiImage } from "react-icons/fi";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { productsAPI } from "@/lib/api";
import { useCart } from "@/contexts/CartContext";
import { formatCurrency } from "@/lib/utils";
import Link from "next/link";

export default function ProductsPage() {
  const { addToCart, cartItems } = useCart();

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [selectedCategory, setSelectedCategory] = useState("all");
  const [searchQuery, setSearchQuery] = useState("");

  // Fetch all products
  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const response = await productsAPI.getAllProducts();

        // Set products from API response
        if (response && response.data && Array.isArray(response.data)) {
          setProducts(response.data);
        } else {
          console.error("Unexpected API response format:", response);
          setProducts([]);
        }
      } catch (err) {
        console.error("Error fetching products:", err);
        setError("Failed to load products. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  // Get unique categories from products
  const categories = ["all"];
  const categorySet = new Set();

  products.forEach((product) => {
    if (product.category && !categorySet.has(product.category)) {
      categorySet.add(product.category);
      categories.push(product.category);
    }
  });

  // Filter products by selected category and search query
  const filteredProducts = products
    .filter((product) => product.is_available)
    .filter(
      (product) =>
        selectedCategory === "all" || product.category === selectedCategory
    )
    .filter(
      (product) =>
        searchQuery.trim() === "" ||
        product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        product.description.toLowerCase().includes(searchQuery.toLowerCase())
    );

  const handleAddToCart = (product) => {
    addToCart(product);
  };

  if (loading) {
    return (
      <div className="space-y-8">
        <div className="h-12 bg-gray-200 rounded w-1/3 animate-pulse"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(9)].map((_, index) => (
            <div
              key={index}
              className="h-64 bg-gray-200 rounded-lg animate-pulse"
            ></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between mb-6">
        <h1 className="text-3xl font-bold">Our Menu</h1>

        <div className="mt-4 md:mt-0 flex flex-col sm:flex-row gap-4">
          <div className="relative flex-1">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <FiSearch className="text-gray-400" />
            </div>
            <input
              type="text"
              placeholder="Search products..."
              className="pl-10 w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-orange-500 focus:border-orange-500"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>

          <Link href="/cart">
            <Button leftIcon={<FiShoppingCart />}>
              {/* Cart ({cartItems.length}) */}
            </Button>
          </Link>
        </div>
      </div>

      {/* Categories */}
      {categories.length > 1 && (
        <div className="border-b border-gray-200 mb-6">
          <div className="flex overflow-x-auto pb-2 space-x-4">
            {categories.map((category) => (
              <button
                key={category}
                className={`py-2 px-4 whitespace-nowrap ${
                  selectedCategory === category
                    ? "text-orange-600 border-b-2 border-orange-600 font-medium"
                    : "text-gray-500 hover:text-gray-700"
                }`}
                onClick={() => setSelectedCategory(category)}
              >
                {category === "all" ? "All Items" : category}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Products */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProducts.map((product) => (
          <Card key={product.id} className="overflow-hidden">
            <div className="relative h-48 bg-gray-100 flex items-center justify-center">
              {/* Use a div with background-image instead of Next.js Image for external URLs */}
              <div
                className="w-full h-full bg-cover bg-center"
                style={{
                  backgroundImage: `url('/images/product-default.jpg')`,
                  backgroundSize: "cover",
                  backgroundPosition: "center",
                }}
              >
                <div className="flex items-center justify-center h-full">
                  <FiImage size={48} className="text-gray-400" />
                </div>
              </div>
            </div>
            <div className="p-4">
              <div className="flex justify-between items-start">
                <h3 className="text-lg font-medium">{product.name}</h3>
                <span className="font-medium text-orange-600">
                  {formatCurrency(product.price)}
                </span>
              </div>
              <p className="text-gray-600 mt-2 line-clamp-2">
                {product.description}
              </p>

              <div className="text-sm text-gray-500 mt-1">
                Hawker: {product.hawker_name}
              </div>

              <div className="flex justify-between items-center mt-4">
                {product.category && (
                  <span className="text-xs bg-gray-100 text-gray-600 px-2 py-1 rounded">
                    {product.category}
                  </span>
                )}
                <Button size="sm" onClick={() => handleAddToCart(product)}>
                  Add to Cart
                </Button>
              </div>
            </div>
          </Card>
        ))}
      </div>

      {filteredProducts.length === 0 && (
        <div className="text-center py-12 bg-gray-50 rounded-lg">
          <p className="text-gray-600 text-lg">No products found.</p>
          <Button
            variant="ghost"
            className="mt-4"
            onClick={() => {
              setSelectedCategory("all");
              setSearchQuery("");
            }}
          >
            Clear Filters
          </Button>
        </div>
      )}
    </div>
  );
}
