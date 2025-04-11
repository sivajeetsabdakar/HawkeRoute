"use client";

import { useState, useEffect } from "react";
import Image from "next/image";
import Link from "next/link";
import { useParams } from "next/navigation";
import { FiMapPin, FiStar, FiPhone, FiClock, FiTruck } from "react-icons/fi";
import ProductCard from "@/components/products/ProductCard";
import Button from "@/components/ui/Button";
import { productsAPI } from "@/lib/api";
import { useCart } from "@/contexts/CartContext";
import { getCurrentPosition, calculateDistance } from "@/lib/location";

export default function HawkerDetailPage() {
  const params = useParams();
  const hawkerId = params.id;
  const { addToCart } = useCart();

  const [hawker, setHawker] = useState(null);
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [userLocation, setUserLocation] = useState(null);
  const [selectedCategory, setSelectedCategory] = useState("all");

  useEffect(() => {
    const fetchHawkerDetails = async () => {
      try {
        setLoading(true);

        // In a real app, we would have a dedicated API for hawker details
        // For now, create mock hawker data
        const mockHawker = {
          id: hawkerId,
          name: `Hawker ${hawkerId}`,
          business_name: `Street Food Vendor ${hawkerId}`,
          business_address: "123 Street Name",
          phone: "+1234567890",
          rating: (3 + Math.random() * 2).toFixed(1),
          total_ratings: Math.floor(Math.random() * 100),
          image_url: "/images/hawker-detail.jpg",
          banner_url: "/images/hawker-banner.jpg",
          specialty: "Street Food",
          description:
            "Delicious authentic street food prepared with fresh ingredients and traditional recipes.",
          working_hours: "10:00 AM - 8:00 PM",
          latitude: 1.2345,
          longitude: 6.789,
        };

        setHawker(mockHawker);

        // Fetch products from this hawker
        const response = await productsAPI.getAllProducts({
          hawker_id: hawkerId,
        });

        // If no products, create mock products
        let productsData = response.data.length > 0 ? response.data : [];

        if (productsData.length === 0) {
          // Create mock products
          const categories = [
            "Main Dishes",
            "Side Dishes",
            "Beverages",
            "Desserts",
          ];
          const mockProducts = [];

          for (let i = 1; i <= 12; i++) {
            const categoryIndex = Math.floor(Math.random() * categories.length);
            mockProducts.push({
              id: i,
              hawker_id: parseInt(hawkerId),
              name: `Product ${i}`,
              description:
                "Delicious street food dish made with fresh ingredients.",
              price: 5 + Math.floor(Math.random() * 15),
              image_url: "/images/product-default.jpg",
              is_available: Math.random() > 0.2, // 80% chance of being available
              category: categories[categoryIndex],
            });
          }

          productsData = mockProducts;
        }

        setProducts(productsData);
      } catch (err) {
        console.error("Error fetching hawker details:", err);
        setError("Failed to load hawker details. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    // Get user's location
    const getUserLocation = async () => {
      try {
        const position = await getCurrentPosition();
        setUserLocation(position);
      } catch (err) {
        console.error("Error getting location:", err);
      }
    };

    fetchHawkerDetails();
    getUserLocation();
  }, [hawkerId]);

  const handleAddToCart = (product) => {
    addToCart(product);
  };

  if (loading) {
    return (
      <div className="space-y-8 animate-pulse">
        <div className="h-64 bg-gray-200 rounded-lg"></div>
        <div className="h-12 bg-gray-200 rounded w-1/3"></div>
        <div className="h-8 bg-gray-200 rounded w-2/3"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[...Array(6)].map((_, index) => (
            <div key={index} className="h-64 bg-gray-200 rounded-lg"></div>
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

  if (!hawker) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-800">Hawker not found</h2>
        <p className="text-gray-600 mt-2">
          The hawker you're looking for doesn't exist.
        </p>
        <Link href="/hawkers">
          <Button className="mt-6">Back to Hawkers</Button>
        </Link>
      </div>
    );
  }

  // Get unique categories from products
  const categories = [
    "all",
    ...new Set(products.map((product) => product.category)),
  ];

  // Filter products by selected category
  const filteredProducts =
    selectedCategory === "all"
      ? products
      : products.filter((product) => product.category === selectedCategory);

  return (
    <div className="space-y-8">
      {/* Hawker Banner */}
      <div className="relative h-64 rounded-lg overflow-hidden">
        <Image
          src={hawker.banner_url || hawker.image_url}
          alt={hawker.business_name}
          fill
          className="object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent flex items-end">
          <div className="p-6 text-white">
            <h1 className="text-3xl font-bold">{hawker.business_name}</h1>
            <div className="flex items-center mt-2">
              <FiMapPin className="mr-1" />
              <span>{hawker.business_address}</span>
            </div>
            <div className="flex items-center mt-2">
              <FiStar className="mr-1 text-yellow-400" />
              <span>{hawker.rating}</span>
              <span className="text-gray-300 ml-1">
                ({hawker.total_ratings} ratings)
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Hawker Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-2">
          <h2 className="text-2xl font-bold mb-4">
            About {hawker.business_name}
          </h2>
          <p className="text-gray-600 mb-6">{hawker.description}</p>

          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-6">
            <div className="flex items-center text-gray-600">
              <FiClock className="mr-2 text-orange-600" />
              <div>
                <p className="font-medium">Working Hours</p>
                <p className="text-sm">{hawker.working_hours}</p>
              </div>
            </div>
            <div className="flex items-center text-gray-600">
              <FiPhone className="mr-2 text-orange-600" />
              <div>
                <p className="font-medium">Contact</p>
                <p className="text-sm">{hawker.phone}</p>
              </div>
            </div>
            <div className="flex items-center text-gray-600">
              <FiTruck className="mr-2 text-orange-600" />
              <div>
                <p className="font-medium">Delivery</p>
                <p className="text-sm">Available</p>
              </div>
            </div>
          </div>

          {userLocation && (
            <div className="bg-orange-50 p-4 rounded-lg mb-6">
              <p className="text-orange-800">
                <span className="font-medium">
                  Distance from your location:
                </span>{" "}
                {calculateDistance(
                  userLocation.latitude,
                  userLocation.longitude,
                  hawker.latitude,
                  hawker.longitude
                ).toFixed(1)}{" "}
                km
              </p>
            </div>
          )}
        </div>

        <div className="relative">
          <Image
            src={hawker.image_url}
            alt={hawker.business_name}
            width={300}
            height={300}
            className="rounded-lg object-cover"
          />
        </div>
      </div>

      {/* Menu Categories */}
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

      {/* Products Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredProducts.map((product) => (
          <ProductCard
            key={product.id}
            product={product}
            onAddToCart={handleAddToCart}
          />
        ))}
      </div>

      {filteredProducts.length === 0 && (
        <div className="text-center py-12">
          <p className="text-gray-600 text-lg">
            No products found in this category.
          </p>
          <Button
            variant="ghost"
            className="mt-4"
            onClick={() => setSelectedCategory("all")}
          >
            View All Products
          </Button>
        </div>
      )}
    </div>
  );
}
