"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import Image from "next/image";
import Card from "@/components/ui/Card";
import Button from "@/components/ui/Button";
import { FiSearch, FiMapPin, FiStar, FiMap, FiList } from "react-icons/fi";
import { locationAPI } from "@/lib/api";
import {
  getCurrentPosition,
  watchPosition,
  calculateDistance,
} from "@/lib/location";

export default function HawkersPage() {
  const router = useRouter();
  const [hawkers, setHawkers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [userLocation, setUserLocation] = useState(null);
  const [viewMode, setViewMode] = useState("list");
  const [radius, setRadius] = useState(5); // Default 5km radius
  const [isWatchingLocation, setIsWatchingLocation] = useState(false);

  useEffect(() => {
    const fetchNearbyHawkers = async () => {
      try {
        setLoading(true);
        if (!userLocation) return;

        const response = await locationAPI.getNearbyHawkers({
          latitude: userLocation.latitude,
          longitude: userLocation.longitude,
          radius: radius * 1000, // Convert km to meters as the API expects meters
        });

        console.log("API response:", response);

        // Handle the specific response format
        if (
          response.data &&
          response.data.status === "success" &&
          Array.isArray(response.data.data)
        ) {
          setHawkers(response.data.data);
        } else if (Array.isArray(response.data)) {
          setHawkers(response.data);
        } else {
          console.error("Unexpected API response format:", response.data);
          setHawkers([]);
          setError("Received invalid data format from server");
        }
      } catch (err) {
        console.error("Error fetching nearby hawkers:", err);
        setError("Failed to load hawkers. Please try again later.");
        setHawkers([]); // Reset to empty array on error
      } finally {
        setLoading(false);
      }
    };

    fetchNearbyHawkers();
  }, [userLocation, radius]);

  useEffect(() => {
    const getUserLocation = async () => {
      try {
        const position = await getCurrentPosition();
        setUserLocation(position);
      } catch (err) {
        console.error("Error getting location:", err);
        setError("Please enable location services to find nearby hawkers.");
      }
    };

    getUserLocation();
  }, []);

  useEffect(() => {
    let clearWatch;
    if (isWatchingLocation && userLocation) {
      clearWatch = watchPosition((position) => {
        setUserLocation(position);
      });
    }

    return () => {
      if (clearWatch) clearWatch();
    };
  }, [isWatchingLocation]);

  // Ensure hawkers is an array before filtering
  const hawkersArray = Array.isArray(hawkers) ? hawkers : [];

  // Filter hawkers based on search term
  const filteredHawkers = hawkersArray.filter(
    (hawker) =>
      (hawker.business_name &&
        hawker.business_name
          .toLowerCase()
          .includes(searchTerm.toLowerCase())) ||
      (hawker.business_address &&
        hawker.business_address
          .toLowerCase()
          .includes(searchTerm.toLowerCase())) ||
      (hawker.specialty &&
        hawker.specialty.toLowerCase().includes(searchTerm.toLowerCase())) ||
      (hawker.name &&
        hawker.name.toLowerCase().includes(searchTerm.toLowerCase()))
  );

  // Hawkers come pre-sorted by distance from the API, but we can sort again if needed
  const sortedHawkers = [...filteredHawkers];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Hawkers Near You</h1>
        <div className="flex items-center space-x-4">
          <div className="relative">
            <input
              type="text"
              placeholder="Search hawkers..."
              className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
            />
            <FiSearch className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
          </div>
          <div className="flex items-center space-x-2">
            <Button
              variant={viewMode === "list" ? "primary" : "ghost"}
              onClick={() => setViewMode("list")}
            >
              <FiList className="mr-2" />
              List
            </Button>
          </div>
        </div>
      </div>

      <div className="flex items-center space-x-4">
        <label className="text-gray-600">Search Radius:</label>
        <select
          value={radius}
          onChange={(e) => setRadius(Number(e.target.value))}
          className="border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500"
        >
          <option value={1}>1 km</option>
          <option value={3}>3 km</option>
          <option value={5}>5 km</option>
          <option value={10}>10 km</option>
        </select>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {loading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {[...Array(6)].map((_, index) => (
            <div
              key={index}
              className="bg-white rounded-lg shadow-md overflow-hidden h-64 animate-pulse"
            >
              <div className="bg-gray-200 h-32"></div>
              <div className="p-4 space-y-3">
                <div className="h-5 bg-gray-200 rounded w-2/3"></div>
                <div className="h-4 bg-gray-200 rounded w-full"></div>
                <div className="h-4 bg-gray-200 rounded w-1/2"></div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <>
          {viewMode === "map" ? (
            <div className="h-[600px] bg-gray-100 rounded-lg">
              {/* Map component will be implemented here */}
              <p className="text-center py-8 text-gray-600">
                Map view coming soon...
              </p>
            </div>
          ) : (
            <>
              {sortedHawkers.length === 0 ? (
                <div className="text-center py-12">
                  <p className="text-gray-600 text-lg">
                    No hawkers found within {radius}km of your location.
                  </p>
                  <Button
                    variant="ghost"
                    className="mt-4"
                    onClick={() => {
                      setSearchTerm("");
                      setRadius(10);
                    }}
                  >
                    Increase Search Radius
                  </Button>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {sortedHawkers.map((hawker) => (
                    <Card key={hawker.id} className="h-full flex flex-col">
                     
                      <div className="flex-grow p-4">
                        <h2 className="text-xl font-semibold mb-2 text-black">
                          {hawker.business_name ||
                            hawker.name ||
                            "Unnamed Hawker"}
                        </h2>
                        
                        {(hawker.rating || hawker.total_ratings) && (
                          <div className="flex items-center text-gray-600 mb-4">
                            <FiStar
                              className="mr-1 text-yellow-500"
                              size={16}
                            />
                            <span>{hawker.rating || "N/A"}</span>
                            {hawker.total_ratings && (
                              <span className="text-sm text-gray-500 ml-1">
                                ({hawker.total_ratings} ratings)
                              </span>
                            )}
                          </div>
                        )}

                        {hawker.products_count && (
                          <p className="text-sm text-gray-500 mb-4">
                            Products: {hawker.products_count}
                          </p>
                        )}

                        <p className="text-sm text-gray-500 mb-4">
                          Distance:{" "}
                          {hawker.distance_km
                            ? hawker.distance_km.toFixed(1)
                            : hawker.distance_m
                            ? (hawker.distance_m / 1000).toFixed(1)
                            : hawker.distance
                            ? (hawker.distance / 1000).toFixed(1)
                            : "N/A"}{" "}
                          km
                        </p>

                        <Link
                          href={`/hawkers/${hawker.id}`}
                          className="block mt-auto"
                        >
                          <Button fullWidth>View Menu</Button>
                        </Link>
                      </div>
                    </Card>
                  ))}
                </div>
              )}
            </>
          )}
        </>
      )}
    </div>
  );
}
