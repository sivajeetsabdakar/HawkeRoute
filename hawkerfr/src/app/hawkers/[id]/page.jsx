"use client";

import { useState, useEffect, useCallback } from "react";
import Image from "next/image";
import Link from "next/link";
import { useParams } from "next/navigation";
import { FiMapPin, FiStar, FiPhone, FiClock, FiTruck, FiMail } from "react-icons/fi";
import ProductCard from "@/components/products/ProductCard";
import Button from "@/components/ui/Button";
import { productsAPI, hawkerAPI, locationAPI } from "@/lib/api";
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

  // Split the fetch logic into separate useEffects
  // 1. First useEffect gets user location only once
  useEffect(() => {
    const getUserLocation = async () => {
      try {
        const position = await getCurrentPosition();
        setUserLocation(position);
      } catch (err) {
        console.error("Error getting location:", err);
      }
    };

    getUserLocation();
  }, []); // Empty dependency array so it only runs once

  // 2. Second useEffect fetches hawker data and products
  useEffect(() => {
    // Skip if we're already loading
    if (!loading && !hawker && !error) return;
    
    const fetchData = async () => {
      try {
        setLoading(true);

        // Fetch hawker profile
        let hawkerData = null;
        try {
          const hawkerResponse = await hawkerAPI.getProfile(hawkerId);
          
          if (hawkerResponse.data && hawkerResponse.data.status === "success") {
            hawkerData = hawkerResponse.data.data;
          } else {
            hawkerData = hawkerResponse.data;
          }
          
          console.log("Hawker data:", hawkerData);
        } catch (err) {
          console.error("Error fetching hawker profile:", err);
          
          // If we get a 404 for the hawker, we'll check if it exists in nearby hawkers
          try {
            if (userLocation) {
              const nearbyResponse = await locationAPI.getNearbyHawkers({
                latitude: userLocation.latitude,
                longitude: userLocation.longitude,
                radius: 50000 // Wider radius to find the hawker (50km)
              });
              
              let nearbyHawkers = [];
              if (nearbyResponse.data && nearbyResponse.data.status === "success") {
                nearbyHawkers = nearbyResponse.data.data;
              } else if (Array.isArray(nearbyResponse.data)) {
                nearbyHawkers = nearbyResponse.data;
              }
              
              const matchingHawker = nearbyHawkers.find(h => String(h.id) === String(hawkerId));
              if (matchingHawker) {
                hawkerData = matchingHawker;
              }
            }
          } catch (nearbyErr) {
            console.error("Error fetching nearby hawkers:", nearbyErr);
          }
        }

        if (hawkerData) {
          setHawker(hawkerData);
        } else {
          setError("Hawker not found. The hawker may no longer be available.");
        }

        // Fetch all products and filter by hawker_id
        try {
          const productsResponse = await productsAPI.getAllProducts({
            hawker_id: hawkerId // Use the query parameter to filter by hawker
          });
          
          let hawkerProducts = [];
          if (productsResponse.data && productsResponse.data.status === "success") {
            hawkerProducts = productsResponse.data.data;
          } else if (Array.isArray(productsResponse.data)) {
            hawkerProducts = productsResponse.data;
          }
          
          console.log("Hawker products:", hawkerProducts);
          
          if (hawkerProducts.length > 0) {
            setProducts(hawkerProducts);
          } else {
            console.log("No products found for this hawker");
          }
        } catch (err) {
          console.error("Error fetching products:", err);
        }
      } catch (err) {
        console.error("Error in hawker details flow:", err);
        setError("Failed to load hawker details. Please try again later.");
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [hawkerId]); // Only depends on hawkerId, not userLocation

  const handleAddToCart = (product) => {
    // Create a simplified product object with only the necessary information
    const simplifiedProduct = {
      id: product.id,
      name: product.name,
      price: product.price,
      hawker_id: hawker.id,
      hawker_name: hawker.business_name || hawker.name
    };

    addToCart(simplifiedProduct);
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
        <div className="mt-4">
          <Link href="/hawkers">
            <Button>Back to Hawkers</Button>
          </Link>
        </div>
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
    ...new Set(products.map((product) => product.category).filter(Boolean)),
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
          src={hawker.banner_url || hawker.image_url || "/images/hawker-default.jpg"}
          alt={hawker.business_name || hawker.name}
          fill
          className="object-cover"
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/70 to-transparent flex items-end">
          <div className="p-6 text-white">
            <h1 className="text-3xl font-bold">{hawker.business_name || hawker.name}</h1>
            {hawker.business_address && (
              <div className="flex items-center mt-2">
                <FiMapPin className="mr-1" />
                <span>{hawker.business_address}</span>
              </div>
            )}
            {(hawker.rating || hawker.total_ratings) && (
              <div className="flex items-center mt-2">
                <FiStar className="mr-1 text-yellow-400" />
                <span>{hawker.rating || "N/A"}</span>
                {hawker.total_ratings && (
                  <span className="text-gray-300 ml-1">
                    ({hawker.total_ratings} ratings)
                  </span>
                )}
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Hawker Info */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
        <div className="md:col-span-2">
          <h2 className="text-2xl font-bold mb-4">
            About {hawker.business_name || hawker.name}
          </h2>
          {hawker.description ? (
            <p className="text-gray-600 mb-6">{hawker.description}</p>
          ) : (
            <p className="text-gray-600 mb-6">
              This hawker offers delicious food. Visit or order to experience their menu.
            </p>
          )}

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mb-6">
            {hawker.working_hours && (
              <div className="flex items-center text-gray-600">
                <FiClock className="mr-2 text-orange-600" />
                <div>
                  <p className="font-medium">Working Hours</p>
                  <p className="text-sm">{hawker.working_hours}</p>
                </div>
              </div>
            )}
            {hawker.phone && (
              <div className="flex items-center text-gray-600">
                <FiPhone className="mr-2 text-orange-600" />
                <div>
                  <p className="font-medium">Contact</p>
                  <p className="text-sm">{hawker.phone}</p>
                </div>
              </div>
            )}
            {hawker.email && (
              <div className="flex items-center text-gray-600">
                <FiMail className="mr-2 text-orange-600" />
                <div>
                  <p className="font-medium">Email</p>
                  <p className="text-sm">{hawker.email}</p>
                </div>
              </div>
            )}
          </div>

          {userLocation && hawker.latitude && hawker.longitude && (
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

        <div className="bg-gray-50 p-4 rounded-lg">
          <h3 className="font-bold text-lg mb-3">Location</h3>
          {hawker.latitude && hawker.longitude ? (
            <div className="aspect-square bg-gray-200 rounded mb-3 flex items-center justify-center">
              {/* Map placeholder - would be replaced with actual map component */}
              <p className="text-gray-500 text-sm text-center p-4">
                Map view coming soon
              </p>
            </div>
          ) : (
            <p className="text-gray-500 mb-3">Location not available</p>
          )}
          
          {hawker.business_address && (
            <div className="mb-3">
              <h4 className="font-medium text-sm">Address:</h4>
              <p className="text-gray-600">{hawker.business_address}</p>
            </div>
          )}
          
          {hawker.latitude && hawker.longitude && (
            <Link href={`https://maps.google.com/?q=${hawker.latitude},${hawker.longitude}`} target="_blank">
              <Button fullWidth variant="outline">Get Directions</Button>
            </Link>
          )}
        </div>
      </div>

      {/* Menu */}
      <div>
        <h2 className="text-2xl font-bold mb-4">Menu</h2>
        
        {/* Categories */}
        {categories.length > 1 && (
          <div className="flex overflow-x-auto space-x-2 pb-4 mb-6 scrollbar-hide">
            {categories.map((category) => (
              <button
                key={category}
                className={`px-4 py-2 rounded-full whitespace-nowrap ${
                  selectedCategory === category
                    ? "bg-orange-500 text-white"
                    : "bg-gray-100 text-gray-800 hover:bg-gray-200"
                }`}
                onClick={() => setSelectedCategory(category)}
              >
                {category === "all" ? "All Items" : category}
              </button>
            ))}
          </div>
        )}
        
        {/* Products */}
        {filteredProducts.length === 0 ? (
          <div className="text-center py-10 bg-gray-50 rounded-lg">
            <p className="text-gray-600">No products available in this category.</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredProducts.map((product) => (
              <ProductCard
                key={product.id}
                product={product}
                onAddToCart={() => handleAddToCart(product)}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
