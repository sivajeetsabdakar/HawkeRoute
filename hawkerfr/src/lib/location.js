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

// Prompt user for manual location input
export const promptForManualLocation = async () => {
  try {
    // This implementation assumes you have a UI component that will handle this
    // You might replace this with your own UI implementation
    const latitude = parseFloat(
      prompt("Please enter your latitude (e.g. 1.3521):")
    );
    const longitude = parseFloat(
      prompt("Please enter your longitude (e.g. 103.8198):")
    );

    if (
      isNaN(latitude) ||
      isNaN(longitude) ||
      latitude < -90 ||
      latitude > 90 ||
      longitude < -180 ||
      longitude > 180
    ) {
      throw new Error(
        "Invalid coordinates. Latitude must be between -90 and 90, and longitude between -180 and 180."
      );
    }

    return {
      latitude,
      longitude,
      accuracy: 1000, // Default accuracy in meters when manually entered
      speed: 0,
      heading: 0,
      isManuallyEntered: true,
    };
  } catch (error) {
    throw new Error(`Failed to get manual location: ${error.message}`);
  }
};

// Get current user location using browser geolocation API
export const getCurrentPosition = async () => {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) {
      reject(new Error("Geolocation is not supported by your browser"));
    } else {
      const handleSuccess = (position) => {
        resolve({
          latitude: position.coords.latitude,
          longitude: position.coords.longitude,
          accuracy: position.coords.accuracy,
          speed: position.coords.speed || 0,
          heading: position.coords.heading || 0,
        });
      };

      const handleError = (error) => {
        let errorMessage;
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMessage =
              "Location access was denied. Please enable location services in your browser settings, refresh the page, and try again.";
            // Try to provide browser-specific instructions
            if (navigator.userAgent.indexOf("Chrome") !== -1) {
              errorMessage +=
                " In Chrome, click the location icon in the address bar and select 'Always allow'.";
            } else if (navigator.userAgent.indexOf("Firefox") !== -1) {
              errorMessage +=
                " In Firefox, click the lock icon in the address bar and set Location Access to 'Allow'.";
            } else if (navigator.userAgent.indexOf("Safari") !== -1) {
              errorMessage +=
                " In Safari, go to Settings > Websites > Location and allow for this website.";
            }
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage =
              "Your location information is currently unavailable. Please check your device's GPS or location services and ensure they are enabled. Then refresh the page and try again.";
            break;
          case error.TIMEOUT:
            errorMessage =
              "Location request timed out. Please check your connection, ensure you're in an area with good GPS signal, and try again.";
            break;
          default:
            errorMessage = `An unknown error occurred: ${error.message}`;
        }
        reject(new Error(errorMessage));
      };

      // Try with high accuracy first
      navigator.geolocation.getCurrentPosition(
        handleSuccess,
        (error) => {
          if (error.code === error.TIMEOUT) {
            // If high accuracy times out, try with lower accuracy
            console.log(
              "High accuracy location timed out, trying with lower accuracy..."
            );
            navigator.geolocation.getCurrentPosition(
              handleSuccess,
              handleError,
              { enableHighAccuracy: false, timeout: 10000, maximumAge: 60000 }
            );
          } else {
            handleError(error);
          }
        },
        { enableHighAccuracy: true, timeout: 5000, maximumAge: 0 }
      );
    }
  });
};

// Watch user position
export const watchPosition = (callback, errorCallback) => {
  if (!navigator.geolocation) {
    throw new Error("Geolocation is not supported by your browser");
  }

  const handleError = (error) => {
    let errorMessage;
    switch (error.code) {
      case error.PERMISSION_DENIED:
        errorMessage =
          "Location access was denied. Please enable location services in your browser settings, refresh the page, and try again.";
        // Try to provide browser-specific instructions
        if (navigator.userAgent.indexOf("Chrome") !== -1) {
          errorMessage +=
            " In Chrome, click the location icon in the address bar and select 'Always allow'.";
        } else if (navigator.userAgent.indexOf("Firefox") !== -1) {
          errorMessage +=
            " In Firefox, click the lock icon in the address bar and set Location Access to 'Allow'.";
        } else if (navigator.userAgent.indexOf("Safari") !== -1) {
          errorMessage +=
            " In Safari, go to Settings > Websites > Location and allow for this website.";
        }
        break;
      case error.POSITION_UNAVAILABLE:
        errorMessage =
          "Your location information is currently unavailable. Please check your device's GPS or location services and ensure they are enabled.";
        break;
      case error.TIMEOUT:
        errorMessage =
          "Location request timed out. Please check your connection, ensure you're in an area with good GPS signal, and try again.";
        break;
      default:
        errorMessage = `An unknown error occurred: ${error.message}`;
    }

    if (errorCallback) {
      errorCallback(new Error(errorMessage));
    } else {
      console.error("Error watching position:", errorMessage);
    }
  };

  // Try to get initial position first to ensure permissions
  navigator.geolocation.getCurrentPosition(
    () => {
      console.log("Location permission granted, starting position watch...");
    },
    handleError,
    { enableHighAccuracy: true }
  );

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
    handleError,
    { enableHighAccuracy: true, timeout: 10000, maximumAge: 1000 }
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
  promptForManualLocation,
};
