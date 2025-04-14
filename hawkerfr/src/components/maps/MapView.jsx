import React, { useState, useEffect, useRef } from "react";
import { getCurrentPosition, watchPosition } from "../../lib/location";
import { locationAPI } from "@/lib/api";

const MapView = ({ onSelectHawker }) => {
  const [userLocation, setUserLocation] = useState(null);
  const [isTracking, setIsTracking] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [markers, setMarkers] = useState([]);
  const [nearbyHawkers, setNearbyHawkers] = useState([]);

  const watchIdRef = useRef(null);
  const mapRef = useRef(null);

  // Load map when user location is available
  useEffect(() => {
    if (userLocation) {
      loadMapbox();
    }
  }, [userLocation]);

  // Get user location on component mount
  useEffect(() => {
    setLoading(true);
    getCurrentPosition()
      .then((position) => {
        setUserLocation({
          latitude: position.latitude,
          longitude: position.longitude,
        });
      })
      .catch((err) => {
        console.error(err);
        setError("Unable to get your location");
        // Fall back to default location (Ahmedabad)
        setUserLocation({
          latitude: 23.022505,
          longitude: 72.571365,
        });
      })
      .finally(() => {
        setLoading(false);
      });

    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
      }
      if (watchIdRef.current) {
        watchIdRef.current();
      }
      // Clean up markers
      markers.forEach((marker) => marker.remove());
    };
  }, []);

  const loadMapbox = () => {
    if (!document.getElementById("mapbox-css")) {
      const link = document.createElement("link");
      link.id = "mapbox-css";
      link.href = "https://api.mapbox.com/mapbox-gl-js/v2.14.1/mapbox-gl.css";
      link.rel = "stylesheet";
      document.head.appendChild(link);
    }

    const script = document.createElement("script");
    script.src = "https://api.mapbox.com/mapbox-gl-js/v2.14.1/mapbox-gl.js";
    script.async = true;
    script.onload = initMap;
    script.onerror = () => {
      setError("Failed to load Mapbox library");
      setLoading(false);
    };
    document.body.appendChild(script);
  };

  const fetchNearbyHawkers = async (latitude, longitude) => {
    try {
      setLoading(true);
      console.log("Fetching nearby hawkers at:", latitude, longitude);
      const response = await locationAPI.getNearbyHawkerss(latitude, longitude);
      console.log("Nearby hawkers response:", response.data);

      // Handle the array response from the API
      const hawkersData = response.data.data || [];
      console.log("Extracted hawkers data:", hawkersData);

      // Parse the data to ensure all fields are in the correct format
      const parsedHawkersData = hawkersData.map((hawker) => ({
        id: hawker.id,
        name: hawker.name || "",
        business_name: hawker.business_name || "",
        latitude: parseFloat(hawker.latitude),
        longitude: parseFloat(hawker.longitude),
        distance: hawker.distance_m || 0,
        distance_km: hawker.distance_km || 0,
        products_count: hawker.products_count,
        category: hawker.category || "",
        rating: hawker.rating || 0,
        business_address: hawker.business_address || "",
      }));

      setNearbyHawkers(parsedHawkersData);
      return parsedHawkersData;
    } catch (err) {
      console.error("Error fetching nearby hawkers:", err);
      setError("Failed to load nearby hawkers. Please try again later.");
      setNearbyHawkers([]);
      return [];
    } finally {
      setLoading(false);
    }
  };

  const initMap = async () => {
    setLoading(true);
    if (!document.getElementById("map-container") || !userLocation) {
      setLoading(false);
      return;
    }

    try {
      window.mapboxgl.accessToken =
        "pk.eyJ1Ijoic2FtYXJ0aDEwMTQiLCJhIjoiY2x5ZHp5bnlnMGI0eDJrcjJpMnBjN2xqaCJ9.sSFq6kROa6sl05GfFfd5Iw";

      // Check if map already exists and remove it
      if (mapRef.current) {
        mapRef.current.remove();
      }

      // Clear existing markers
      markers.forEach((marker) => marker.remove());
      setMarkers([]);

      mapRef.current = new window.mapboxgl.Map({
        container: "map-container",
        style: "mapbox://styles/mapbox/streets-v12",
        center: [userLocation.longitude, userLocation.latitude],
        zoom: 13,
      });

      mapRef.current.on("load", async () => {
        // Add user marker
        const userMarkerEl = document.createElement("div");
        userMarkerEl.className = "user-marker";
        userMarkerEl.style.backgroundImage =
          "url(https://docs.mapbox.com/mapbox-gl-js/assets/custom_marker.png)";
        userMarkerEl.style.width = "30px";
        userMarkerEl.style.height = "30px";
        userMarkerEl.style.backgroundSize = "100%";
        userMarkerEl.style.borderRadius = "50%";
        userMarkerEl.style.border = "3px solid #3b82f6";

        new window.mapboxgl.Marker(userMarkerEl)
          .setLngLat([userLocation.longitude, userLocation.latitude])
          .setPopup(
            new window.mapboxgl.Popup().setHTML("<strong>You are here</strong>")
          )
          .addTo(mapRef.current);

        try {
          // Fetch nearby hawkers based on user location
          const hawkersData = await fetchNearbyHawkers(
            userLocation.latitude,
            userLocation.longitude
          );

          if (hawkersData.length === 0) {
            console.log("No nearby hawkers found");
            setLoading(false);
            return;
          }

          console.log("Adding markers for hawkers:", hawkersData);

          // Add hawker markers
          const newMarkers = [];
          hawkersData.forEach((hawker) => {
            if (!hawker.latitude || !hawker.longitude) {
              console.warn("Hawker missing coordinates:", hawker);
              return;
            }

            console.log(
              `Adding marker for ${hawker.business_name} at [${hawker.longitude}, ${hawker.latitude}]`
            );

            // Create custom marker element with business name
            const el = document.createElement("div");
            el.className = "hawker-marker";
            el.style.position = "relative";
            el.style.width = "40px";
            el.style.height = "40px";
            el.style.cursor = "pointer";

            // Create marker pin
            const pin = document.createElement("div");
            pin.style.backgroundImage =
              "url(https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678111-map-marker-512.png)";
            pin.style.width = "40px";
            pin.style.height = "40px";
            pin.style.backgroundSize = "100%";
            pin.style.position = "absolute";
            pin.style.top = "0";
            pin.style.left = "0";
            el.appendChild(pin);

            // Create business name label
            const label = document.createElement("div");
            label.textContent = hawker.business_name || hawker.name;
            label.style.position = "absolute";
            label.style.top = "40px";
            label.style.left = "50%";
            label.style.transform = "translateX(-50%)";
            label.style.whiteSpace = "nowrap";
            label.style.backgroundColor = "rgba(255, 255, 255, 0.8)";
            label.style.padding = "2px 4px";
            label.style.borderRadius = "4px";
            label.style.fontSize = "10px";
            label.style.fontWeight = "bold";
            label.style.textAlign = "center";
            label.style.boxShadow = "0 1px 2px rgba(0,0,0,0.2)";
            el.appendChild(label);

            // Format distance - use API provided distance if available
            const distanceInKm = hawker.distance_km || hawker.distance / 1000;

            // Create popup with hawker info
            const popupContent = `
              <div style="max-width: 200px;">
                <strong>${hawker.business_name || hawker.name}</strong><br>
                ${
                  hawker.business_address
                    ? `<small>${hawker.business_address}</small><br>`
                    : ""
                }
                ${hawker.category ? `<span>${hawker.category}</span><br>` : ""}
                ${
                  hawker.rating
                    ? `<span>Rating: ${hawker.rating}⭐</span><br>`
                    : ""
                }
                <span>~${distanceInKm.toFixed(1)} km away</span>
                ${
                  hawker.products_count
                    ? `<br><small>${hawker.products_count} products available</small>`
                    : ""
                }
              </div>
            `;

            const popup = new window.mapboxgl.Popup({
              offset: 25,
              closeButton: false,
              maxWidth: "300px",
            }).setHTML(popupContent);

            // Create and add the marker
            const marker = new window.mapboxgl.Marker(el)
              .setLngLat([hawker.longitude, hawker.latitude])
              .setPopup(popup)
              .addTo(mapRef.current);

            // Add click event to marker
            el.addEventListener("click", () => {
              if (onSelectHawker) {
                const hawkerWithDistance = {
                  ...hawker,
                  distance: parseFloat(distanceInKm.toFixed(1)),
                };
                onSelectHawker(hawkerWithDistance);
              }
            });

            newMarkers.push(marker);
          });

          // Adjust map bounds to include all markers
          if (newMarkers.length > 0) {
            const bounds = new window.mapboxgl.LngLatBounds();

            // Add user location to bounds
            bounds.extend([userLocation.longitude, userLocation.latitude]);

            // Add all hawker locations to bounds
            hawkersData.forEach((hawker) => {
              if (hawker.latitude && hawker.longitude) {
                bounds.extend([hawker.longitude, hawker.latitude]);
              }
            });

            // Fit map to bounds with padding
            mapRef.current.fitBounds(bounds, {
              padding: { top: 50, bottom: 50, left: 50, right: 50 },
              maxZoom: 15,
            });
          }

          setMarkers(newMarkers);
        } catch (error) {
          console.error("Error adding hawker markers:", error);
        } finally {
          setLoading(false);
        }
      });
    } catch (error) {
      console.error("Error initializing map:", error);
      setError("Failed to initialize map");
      setLoading(false);
    }
  };

  // Calculate distance between two points using Haversine formula
  const calculateDistance = (lat1, lon1, lat2, lon2) => {
    const R = 6371; // Radius of the earth in km
    const dLat = deg2rad(lat2 - lat1);
    const dLon = deg2rad(lon2 - lon1);
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(deg2rad(lat1)) *
        Math.cos(deg2rad(lat2)) *
        Math.sin(dLon / 2) *
        Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    const distance = R * c; // Distance in km
    return distance;
  };

  const deg2rad = (deg) => {
    return deg * (Math.PI / 180);
  };

  const toggleTracking = () => {
    if (isTracking) {
      if (watchIdRef.current) {
        watchIdRef.current();
        watchIdRef.current = null;
      }
      setIsTracking(false);
    } else {
      const clearWatch = watchPosition(
        (pos) => {
          setUserLocation({
            latitude: pos.latitude,
            longitude: pos.longitude,
          });
          if (mapRef.current) {
            mapRef.current.flyTo({
              center: [pos.longitude, pos.latitude],
              essential: true,
            });
          }
        },
        (err) => {
          console.error(err);
          setError("Failed to track location");
        }
      );
      watchIdRef.current = clearWatch;
      setIsTracking(true);
    }
  };

  return (
    <div className="h-full w-full">
      <div className="mb-2 text-center">
        {userLocation ? (
          <p className="text-sm text-gray-700 font-medium">
            📍 Your Location: Latitude - {userLocation.latitude.toFixed(4)},
            Longitude - {userLocation.longitude.toFixed(4)}
          </p>
        ) : (
          <p className="text-sm text-gray-500">Getting your location...</p>
        )}
      </div>

      <div className="relative h-96 mb-4 rounded-lg overflow-hidden">
        {loading ? (
          <div className="flex items-center justify-center h-full bg-gray-100">
            <p className="text-lg font-medium">Loading map...</p>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center h-full text-red-600">
            <p>{error}</p>
          </div>
        ) : (
          <>
            <div
              id="map-container"
              className="w-full h-full"
              style={{ height: "100%", minHeight: "350px" }}
            />
            <div className="absolute bottom-4 right-4 z-10">
              <button
                onClick={toggleTracking}
                className={`px-4 py-2 rounded-full text-white ${
                  isTracking ? "bg-red-500" : "bg-blue-500"
                }`}
              >
                {isTracking ? "Stop Tracking" : "Track Me"}
              </button>
            </div>
          </>
        )}
      </div>

      {nearbyHawkers.length > 0 && (
        <div className="mt-4">
          <h3 className="text-lg font-semibold mb-2 text-black">Nearby Hawkers</h3>
          <div className="space-y-2">
            {nearbyHawkers.map((hawker) => {
              if (!userLocation || !hawker.latitude || !hawker.longitude)
                return null;

              // Use API-provided distance if available
              const distance = hawker.distance_km || hawker.distance / 1000;

              return (
                <div
                  key={hawker.id}
                  className="p-3 bg-white rounded-lg border border-gray-200 shadow-sm hover:bg-blue-50 cursor-pointer text-black"
                  onClick={() =>
                    onSelectHawker &&
                    onSelectHawker({
                      ...hawker,
                      distance: parseFloat(distance.toFixed(1)),
                    })
                  }
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <h4 className="font-medium">
                        {hawker.business_name || hawker.name}
                      </h4>
                      <p className="text-sm text-gray-600">
                        {hawker.business_address || hawker.category || ""}
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">
                        {distance.toFixed(1)} km
                      </p>
                    
                    </div>
                  </div>
                  {hawker.products_count > 0 && (
                    <p className="text-xs text-gray-500 mt-1">
                      {hawker.products_count} products available
                    </p>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default MapView;
