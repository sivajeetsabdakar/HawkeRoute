import React, { useState, useEffect } from "react";
import {
  getCurrentPosition,
  watchPosition,
  formatCoordinates,
} from "../../lib/location";

const LocationAccess = () => {
  const [location, setLocation] = useState(null);
  const [watchId, setWatchId] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  // Get current location once
  const handleGetLocation = async () => {
    setLoading(true);
    setError(null);

    try {
      const position = await getCurrentPosition();
      setLocation(position);
      console.log("Got current position:", position);
    } catch (err) {
      setError(err.message);
      console.error("Error getting location:", err);
    } finally {
      setLoading(false);
    }
  };

  // Start watching location updates
  const startWatchingLocation = () => {
    if (watchId) return; // Already watching

    setError(null);

    try {
      // Handle position updates
      const handlePositionUpdate = (position) => {
        setLocation(position);
        setError(null);
        console.log("Position updated:", position);
      };

      // Handle errors during watch
      const handleWatchError = (err) => {
        setError(err.message);
        console.error("Watch position error:", err);
      };

      // Start watching
      const clearWatch = watchPosition(handlePositionUpdate, handleWatchError);
      setWatchId(() => clearWatch); // Store the function to clear the watch
    } catch (err) {
      setError(err.message);
      console.error("Error starting location watch:", err);
    }
  };

  // Stop watching location
  const stopWatchingLocation = () => {
    if (watchId) {
      watchId(); // Execute the clearWatch function
      setWatchId(null);
      console.log("Location watching stopped");
    }
  };

  // Clean up on unmount
  useEffect(() => {
    return () => {
      if (watchId) {
        watchId(); // Clear the watch when component unmounts
      }
    };
  }, [watchId]);

  return (
    <div className="p-4 border rounded-lg shadow-md">
      <h2 className="text-xl font-bold mb-4">Location Access</h2>

      {/* Error message */}
      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded-md">
          <p className="font-semibold">Error:</p>
          <p>{error}</p>
        </div>
      )}

      {/* Location data */}
      {location && (
        <div className="mb-4 p-3 bg-green-100 text-green-800 rounded-md">
          <p className="font-semibold">Your current location:</p>
          <p>
            Coordinates:{" "}
            {formatCoordinates(location.latitude, location.longitude)}
          </p>
          <p>Latitude: {location.latitude.toFixed(6)}</p>
          <p>Longitude: {location.longitude.toFixed(6)}</p>
          <p>Accuracy: {Math.round(location.accuracy)} meters</p>
          {location.speed > 0 && (
            <p>Speed: {(location.speed * 3.6).toFixed(1)} km/h</p>
          )}
          {location.heading > 0 && (
            <p>Heading: {Math.round(location.heading)}°</p>
          )}
        </div>
      )}

      {/* Action buttons */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={handleGetLocation}
          disabled={loading}
          className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600 disabled:bg-blue-300"
        >
          {loading ? "Getting location..." : "Get Current Location"}
        </button>

        {!watchId ? (
          <button
            onClick={startWatchingLocation}
            className="px-4 py-2 bg-green-500 text-white rounded-md hover:bg-green-600"
          >
            Start Location Tracking
          </button>
        ) : (
          <button
            onClick={stopWatchingLocation}
            className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
          >
            Stop Location Tracking
          </button>
        )}
      </div>
    </div>
  );
};

export default LocationAccess;
