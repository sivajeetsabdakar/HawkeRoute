"use client";

import { useState, useEffect, useCallback } from "react";
import { FiMapPin } from "react-icons/fi";

// A simple Google Maps implementation using iframe
export default function GoogleMap({ latitude, longitude, height = "100%", width = "100%", zoom = 15 }) {
  const [mapUrl, setMapUrl] = useState("");
  const [error, setError] = useState(false);
  
  // Create the map URL
  useEffect(() => {
    if (!latitude || !longitude) {
      setError(true);
      return;
    }
    
    try {
      // Create the Google Maps embed URL
      const url = `https://www.google.com/maps/embed/v1/place?key=YOUR_API_KEY&q=${latitude},${longitude}&zoom=${zoom}`;
      setMapUrl(url);
      setError(false);
    } catch (err) {
      console.error("Error creating map URL:", err);
      setError(true);
    }
  }, [latitude, longitude, zoom]);
  
  // Alternative map rendering if API key is not available
  const renderStaticMap = useCallback(() => {
    return (
      <div className="relative w-full h-full bg-gray-100 flex items-center justify-center rounded overflow-hidden">
        <div className="absolute">
          <FiMapPin className="text-orange-500" size={32} />
        </div>
        <div className="absolute bottom-2 left-2 right-2 bg-white bg-opacity-75 p-2 rounded text-xs text-center">
          <p>Coordinates: {latitude}, {longitude}</p>
          <a 
            href={`https://maps.google.com/?q=${latitude},${longitude}`}
            target="_blank" 
            rel="noopener noreferrer"
            className="text-orange-500 hover:underline"
          >
            Open in Google Maps
          </a>
        </div>
      </div>
    );
  }, [latitude, longitude]);
  
  if (error || !mapUrl.includes("key=YOUR_API_KEY")) {
    return renderStaticMap();
  }
  
  return (
    <iframe
      width={width}
      height={height}
      style={{ border: 0, borderRadius: "0.375rem" }}
      loading="lazy"
      allowFullScreen
      referrerPolicy="no-referrer-when-downgrade"
      src={mapUrl}
    ></iframe>
  );
} 