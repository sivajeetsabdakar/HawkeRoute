// Calculates the distance between two points in km using the Haversine formula
export const calculateDistance = (lat1, lon1, lat2, lon2) => {
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
  const d = R * c; // Distance in km
  return d;
};

// Convert degrees to radians
const deg2rad = (deg) => {
  return deg * (Math.PI / 180);
};

// Get current user location using browser geolocation API
export const getCurrentPosition = () => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("Geolocation is not supported by your browser"));
    } else {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          resolve({
            latitude: position.coords.latitude,
            longitude: position.coords.longitude,
            accuracy: position.coords.accuracy,
            speed: position.coords.speed || 0,
            heading: position.coords.heading || 0,
          });
        },
        (error) => {
          reject(error);
        },
        { enableHighAccuracy: true }
      );
    }
  });
};

// Watch user position
export const watchPosition = (callback) => {
  if (!navigator.geolocation) {
    throw new Error("Geolocation is not supported by your browser");
  }

  const watchId = navigator.geolocation.watchPosition(
    (position) => {
      callback({
        latitude: position.coords.latitude,
        longitude: position.coords.longitude,
        accuracy: position.coords.accuracy,
        speed: position.coords.speed || 0,
        heading: position.coords.heading || 0,
      });
    },
    (error) => {
      console.error("Error watching position:", error);
    },
    { enableHighAccuracy: true }
  );

  // Return a function to clear the watch
  return () => {
    navigator.geolocation.clearWatch(watchId);
  };
};

// Format coordinates for display
export const formatCoordinates = (latitude, longitude) => {
  const lat = Math.abs(latitude).toFixed(4) + (latitude >= 0 ? "°N" : "°S");
  const lng = Math.abs(longitude).toFixed(4) + (longitude >= 0 ? "°E" : "°W");
  return `${lat}, ${lng}`;
};

export default {
  calculateDistance,
  getCurrentPosition,
  watchPosition,
  formatCoordinates,
};
