import React, { useState, useEffect, useRef } from "react";
import { getCurrentPosition, watchPosition } from "../../lib/location";
import mapboxgl from "mapbox-gl";
import "mapbox-gl/dist/mapbox-gl.css";

const MapView = ({ hawkers = [], onSelectHawker }) => {
  const [userLocation, setUserLocation] = useState(null);
  const [isTracking, setIsTracking] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [markers, setMarkers] = useState([]);

  const watchIdRef = useRef(null);
  const mapRef = useRef(null);

  // Mock coordinates for hawkers - in a real app, these would come from the database
  const hawkerLocations = [
    { id: 1, latitude: 23.025473, longitude: 72.503236 }, // Manek Chowk
    { id: 2, latitude: 23.031271, longitude: 72.566588 }, // Law Garden
    { id: 3, latitude: 23.025869, longitude: 72.579977 }, // Bhatiyar Gali
    { id: 4, latitude: 23.045919, longitude: 72.530684 }, // Alpha One
    { id: 5, latitude: 23.00714, longitude: 72.596169 }, // Kankaria Lake
  ];

  useEffect(() => {
    mapboxgl.accessToken =
      "pk.eyJ1Ijoic2FtYXJ0aDEwMTQiLCJhIjoiY2x5ZHp5bnlnMGI0eDJrcjJpMnBjN2xqaCJ9.sSFq6kROa6sl05GfFfd5Iw";

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

  useEffect(() => {
    if (!userLocation || !document.getElementById("map-container")) return;

    try {
      mapRef.current = new mapboxgl.Map({
        container: "map-container",
        style: "mapbox://styles/mapbox/streets-v12",
        center: [userLocation.longitude, userLocation.latitude],
        zoom: 13,
      });

      mapRef.current.on("load", () => {
        // Add user marker
        const userMarkerEl = document.createElement("div");
        userMarkerEl.className =
          "w-[30px] h-[30px] bg-cover rounded-full border-[3px] border-blue-500";
        userMarkerEl.style.backgroundImage =
          "url(https://docs.mapbox.com/mapbox-gl-js/assets/custom_marker.png)";

        new mapboxgl.Marker(userMarkerEl)
          .setLngLat([userLocation.longitude, userLocation.latitude])
          .setPopup(
            new mapboxgl.Popup().setHTML("<strong>You are here</strong>")
          )
          .addTo(mapRef.current);

        // Add hawker markers
        const newMarkers = [];
        hawkerLocations.forEach((location, index) => {
          if (index < hawkers.length) {
            const hawker = hawkers[index];

            // Calculate distance from user (simplified formula)
            const distance = calculateDistance(
              userLocation.latitude,
              userLocation.longitude,
              location.latitude,
              location.longitude
            );

            // Create marker element
            const el = document.createElement("div");
            el.className = "w-[40px] h-[40px] bg-cover";
            el.style.backgroundImage =
              "url(https://cdn0.iconfinder.com/data/icons/small-n-flat/24/678111-map-marker-512.png)";

            // Create popup with hawker info
            const popup = new mapboxgl.Popup({ offset: 25 }).setHTML(
              `<strong>${hawker.name}</strong><br>
              ${hawker.category}<br>
              Rating: ${hawker.rating}⭐<br>
              ~${distance.toFixed(1)} km away`
            );

            // Create and add the marker
            const marker = new mapboxgl.Marker(el)
              .setLngLat([location.longitude, location.latitude])
              .setPopup(popup)
              .addTo(mapRef.current);

            // Add click event to marker
            el.addEventListener("click", () => {
              onSelectHawker({
                ...hawker,
                distance,
                latitude: location.latitude,
                longitude: location.longitude,
              });
            });

            newMarkers.push(marker);
          }
        });

        setMarkers(newMarkers);
        setLoading(false);
      });
    } catch (err) {
      console.error("Map initialization error:", err);
      setError("Failed to initialize map");
      setLoading(false);
    }
  }, [userLocation, hawkers, onSelectHawker]);

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
            <div id="map-container" className="w-full h-full min-h-[350px]" />
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

      {hawkers.length > 0 && (
        <div className="mt-4">
          <h3 className="text-lg font-semibold mb-2">Nearby Hawkers</h3>
          <div className="space-y-2">
            {hawkers.map((hawker, index) => {
              const location = hawkerLocations[index];
              if (!location || !userLocation) return null;

              const distance = calculateDistance(
                userLocation.latitude,
                userLocation.longitude,
                location.latitude,
                location.longitude
              );

              return (
                <div
                  key={hawker.id}
                  className="p-3 bg-white rounded-lg border border-gray-200 shadow-sm hover:bg-blue-50 cursor-pointer"
                  onClick={() =>
                    onSelectHawker({
                      ...hawker,
                      distance,
                      latitude: location.latitude,
                      longitude: location.longitude,
                    })
                  }
                >
                  <div className="flex justify-between items-center">
                    <div>
                      <h4 className="font-medium">{hawker.name}</h4>
                      <p className="text-sm text-gray-600">{hawker.category}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-medium">
                        {distance.toFixed(1)} km
                      </p>
                      <p className="text-yellow-500">
                        {"★".repeat(Math.floor(hawker.rating))}
                      </p>
                    </div>
                  </div>
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
