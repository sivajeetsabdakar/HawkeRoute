"use client";

import React, { useState, useEffect } from "react";
import MapView from "../../components/maps/MapView";

const LocationPage = () => {
  // Mock data for hawkers - in a real app, this would come from an API or state management
  const [hawkers, setHawkers] = useState([
    {
      id: 1,
      name: "Manek Chowk Food Street",
      category: "Street Food",
      rating: 4.7,
    },
    {
      id: 2,
      name: "Law Garden Food Stalls",
      category: "Street Food",
      rating: 4.5,
    },
    { id: 3, name: "Bhatiyar Gali", category: "Food Street", rating: 4.3 },
    {
      id: 4,
      name: "Alpha One Food Court",
      category: "Food Court",
      rating: 4.1,
    },
    {
      id: 5,
      name: "Kankaria Lake Food Zone",
      category: "Food Court",
      rating: 4.4,
    },
  ]);

  const [selectedHawker, setSelectedHawker] = useState(null);
  const [permissionStatus, setPermissionStatus] = useState("unknown"); // unknown, granted, denied, prompt

  // Check permission status on component mount
  useEffect(() => {
    checkLocationPermission();
  }, []);

  // Function to check the current location permission status
  const checkLocationPermission = async () => {
    if (!navigator.permissions || !navigator.permissions.query) {
      // Browser doesn't support permissions API, we'll have to try to get location directly
      setPermissionStatus("unknown");
      return;
    }

    try {
      const permissionResult = await navigator.permissions.query({
        name: "geolocation",
      });

      setPermissionStatus(permissionResult.state); // "granted", "denied", or "prompt"

      // Listen for changes to permission state
      permissionResult.onchange = () => {
        setPermissionStatus(permissionResult.state);
      };
    } catch (error) {
      console.error("Error checking location permission:", error);
      setPermissionStatus("unknown");
    }
  };

  // Function to request location permission
  const requestLocationPermission = () => {
    // The simplest way to prompt for permission is to request the position
    navigator.geolocation.getCurrentPosition(
      // Success callback
      () => {
        setPermissionStatus("granted");
        checkLocationPermission(); // Recheck permission after request
      },
      // Error callback
      (error) => {
        if (error.code === error.PERMISSION_DENIED) {
          setPermissionStatus("denied");
        }
        console.error("Permission request failed:", error);
      }
    );
  };

  // Function to provide browser-specific instructions
  const getBrowserInstructions = () => {
    const userAgent = navigator.userAgent;

    if (userAgent.indexOf("Chrome") !== -1) {
      return (
        <div className="mt-2">
          <p className="font-semibold">To enable in Chrome:</p>
          <ol className="list-decimal pl-5 mt-1">
            <li>Click the lock icon (or ⓘ) in the address bar</li>
            <li>Click on "Location"</li>
            <li>Select "Allow"</li>
            <li>Refresh the page</li>
          </ol>
        </div>
      );
    } else if (userAgent.indexOf("Firefox") !== -1) {
      return (
        <div className="mt-2">
          <p className="font-semibold">To enable in Firefox:</p>
          <ol className="list-decimal pl-5 mt-1">
            <li>Click the lock icon in the address bar</li>
            <li>Click "Clear Permissions"</li>
            <li>Refresh the page and click "Allow" when prompted</li>
          </ol>
        </div>
      );
    } else if (userAgent.indexOf("Safari") !== -1) {
      return (
        <div className="mt-2">
          <p className="font-semibold">To enable in Safari:</p>
          <ol className="list-decimal pl-5 mt-1">
            <li>Go to Safari preferences</li>
            <li>Click "Websites" tab, then "Location"</li>
            <li>Find this website and select "Allow"</li>
            <li>Refresh the page</li>
          </ol>
        </div>
      );
    } else if (userAgent.indexOf("Edge") !== -1) {
      return (
        <div className="mt-2">
          <p className="font-semibold">To enable in Edge:</p>
          <ol className="list-decimal pl-5 mt-1">
            <li>Click the lock icon in the address bar</li>
            <li>Click "Site permissions"</li>
            <li>Turn on "Location" permission</li>
            <li>Refresh the page</li>
          </ol>
        </div>
      );
    }

    return (
      <div className="mt-2">
        <p className="font-semibold">To enable location access:</p>
        <ol className="list-decimal pl-5 mt-1">
          <li>Check your browser settings</li>
          <li>Look for site permissions or privacy settings</li>
          <li>Allow location access for this website</li>
          <li>Refresh the page</li>
        </ol>
      </div>
    );
  };

  const handleSelectHawker = (hawker) => {
    setSelectedHawker(hawker);
  };

  // Permission prompt component
  const renderPermissionPrompt = () => {
    if (permissionStatus === "denied") {
      return (
        <div className="bg-yellow-50 border-2 border-yellow-200 p-6 rounded-lg text-center mb-6">
          <h2 className="text-xl font-bold text-yellow-800 mb-2">
            Location Access Blocked
          </h2>
          <p className="mb-4">
            You've blocked location access for this site. We'll show you hawkers
            near Ahmedabad, India, but to see hawkers near your own location,
            please allow access.
          </p>

          {getBrowserInstructions()}

          <button
            onClick={checkLocationPermission}
            className="mt-4 bg-yellow-600 text-white px-4 py-2 rounded-md hover:bg-yellow-700"
          >
            I've Enabled Access, Try Again
          </button>
        </div>
      );
    }

    if (permissionStatus === "prompt" || permissionStatus === "unknown") {
      return (
        <div className="bg-blue-50 border-2 border-blue-200 p-6 rounded-lg text-center mb-6">
          <h2 className="text-xl font-bold text-blue-800 mb-2">
            Location Access Required
          </h2>
          <p className="mb-4">
            To show you nearby hawkers, we need access to your location. Please
            click the button below and allow location access when prompted. If
            denied, we'll show you hawkers near Ahmedabad, India.
          </p>
          <button
            onClick={requestLocationPermission}
            className="mt-2 bg-blue-600 text-white px-6 py-3 rounded-md hover:bg-blue-700 font-semibold"
          >
            Allow Location Access
          </button>
        </div>
      );
    }

    return null;
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Find Nearby Hawkers</h1>

      {/* Permission prompt */}
      {renderPermissionPrompt()}

      <div className="bg-white rounded-lg shadow-md overflow-hidden">
        <div className="p-4 border-b">
          <h2 className="text-lg font-semibold text-black">Your Location</h2>
          <p className="text-sm text-gray-600">
            We need your location to show you nearby hawkers. Make sure location
            services are enabled in your browser. Otherwise, we'll show you
            hawkers near Ahmedabad, India (23.228972, 72.675712).
          </p>
        </div>

        <div className="p-4">
          <MapView hawkers={hawkers} onSelectHawker={handleSelectHawker} />
        </div>
      </div>

      {/* Hawker Details Modal */}
      {selectedHawker && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-md w-full p-6">
            <div className="flex justify-between items-start mb-4">
              <h3 className="text-xl font-bold">{selectedHawker.name}</h3>
              <button
                onClick={() => setSelectedHawker(null)}
                className="text-gray-500 hover:text-gray-700"
              >
                ✕
              </button>
            </div>

            <div className="mb-4">
              <p className="text-gray-600">{selectedHawker.category}</p>
              <p className="flex items-center mt-1">
                <span className="text-yellow-500 mr-1">★</span>
                <span>{selectedHawker.rating}</span>
              </p>
              {selectedHawker.distance && (
                <p className="mt-1 text-blue-600">
                  {selectedHawker.distance.toFixed(1)} km away
                </p>
              )}
            </div>

            <div className="flex justify-end">
              <button
                onClick={() =>
                  window.alert(`Directions to ${selectedHawker.name}`)
                }
                className="bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600"
              >
                Get Directions
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default LocationPage;
