"use client";

import { useState, useEffect } from "react";
import { FiMapPin, FiNavigation, FiCrosshair, FiChevronRight, FiChevronLeft } from "react-icons/fi";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import StaticMap from "@/components/maps/StaticMap";
import toast from "react-hot-toast";

const PREDEFINED_LOCATIONS = [
  { name: "Singapore", latitude: 1.3521, longitude: 103.8198 },
  { name: "Kuala Lumpur", latitude: 3.1390, longitude: 101.6869 },
  { name: "Jakarta", latitude: -6.2088, longitude: 106.8456 },
  { name: "Bangkok", latitude: 13.7563, longitude: 100.5018 },
  { name: "Manila", latitude: 14.5995, longitude: 120.9842 },
  { name: "Tokyo", latitude: 35.6762, longitude: 139.6503 },
  { name: "Seoul", latitude: 37.5665, longitude: 126.9780 },
  { name: "New York", latitude: 40.7128, longitude: -74.0060 },
  { name: "London", latitude: 51.5074, longitude: -0.1278 },
  { name: "Sydney", latitude: -33.8688, longitude: 151.2093 }
];

export default function MapTest() {
  const [coordinates, setCoordinates] = useState({
    latitude: 1.3521,
    longitude: 103.8198
  });
  const [currentLocationIndex, setCurrentLocationIndex] = useState(0);
  const [userLocation, setUserLocation] = useState(null);
  const [mapDetails, setMapDetails] = useState({
    viewingError: false,
    loadTime: null
  });
  
  // Load user's location on component mount
  useEffect(() => {
    const getUserLocation = async () => {
      if (!navigator.geolocation) {
        toast.error("Geolocation is not supported by your browser");
        return;
      }
      
      try {
        navigator.geolocation.getCurrentPosition(
          (position) => {
            const { latitude, longitude } = position.coords;
            setUserLocation({ latitude, longitude });
            toast.success("Your location was detected successfully");
          },
          (error) => {
            console.error("Error getting location:", error);
            toast.error(`Could not get your location: ${error.message}`);
          }
        );
      } catch (error) {
        console.error("Geolocation error:", error);
      }
    };
    
    getUserLocation();
  }, []);
  
  // Function to cycle through predefined locations
  const cycleLocation = (direction) => {
    let newIndex;
    if (direction === 'next') {
      newIndex = (currentLocationIndex + 1) % PREDEFINED_LOCATIONS.length;
    } else {
      newIndex = (currentLocationIndex - 1 + PREDEFINED_LOCATIONS.length) % PREDEFINED_LOCATIONS.length;
    }
    
    setCurrentLocationIndex(newIndex);
    setCoordinates({
      latitude: PREDEFINED_LOCATIONS[newIndex].latitude,
      longitude: PREDEFINED_LOCATIONS[newIndex].longitude
    });
    
    toast.success(`Showing ${PREDEFINED_LOCATIONS[newIndex].name}`);
  };
  
  // Function to use user's location
  const useMyLocation = () => {
    if (!userLocation) {
      toast.error("Your location is not available");
      return;
    }
    
    setCoordinates({
      latitude: userLocation.latitude,
      longitude: userLocation.longitude
    });
    
    toast.success("Map updated to your current location");
  };
  
  // Function to simulate map errors
  const simulateMapError = () => {
    setMapDetails(prev => ({ ...prev, viewingError: true }));
    toast.error("Simulating map error state");
    
    // Reset after 3 seconds
    setTimeout(() => {
      setMapDetails(prev => ({ ...prev, viewingError: false }));
      toast.success("Map error state reset");
    }, 3000);
  };
  
  // Function to test map loading time
  const testMapLoadTime = () => {
    const startTime = performance.now();
    
    // Set random coordinates to force a re-render
    const randomOffset = (Math.random() - 0.5) * 0.01;
    setCoordinates({
      latitude: coordinates.latitude + randomOffset,
      longitude: coordinates.longitude + randomOffset
    });
    
    // Measure time after the next render
    setTimeout(() => {
      const endTime = performance.now();
      const loadTime = endTime - startTime;
      setMapDetails(prev => ({ ...prev, loadTime }));
      toast.success(`Map loaded in ${loadTime.toFixed(2)}ms`);
    }, 100);
  };
  
  return (
    <div className="space-y-8 pb-12">
      <div className="border-b border-gray-200 pb-5 mb-5">
        <h1 className="text-3xl font-bold text-white">Map Component Testing</h1>
        <p className="mt-2 text-sm text-gray-800">
          Test the map component with various locations and scenarios
        </p>
      </div>
      
      {/* Current Location Display */}
      <Card>
        <h2 className="text-xl font-semibold mb-4 text-black">Current Location</h2>
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="font-medium text-black">{PREDEFINED_LOCATIONS[currentLocationIndex].name}</p>
            <p className="text-sm text-gray-800">
              Lat: {coordinates.latitude.toFixed(6)}, Long: {coordinates.longitude.toFixed(6)}
            </p>
          </div>
          <div className="flex gap-2">
            <Button size="sm" variant="outline" onClick={() => cycleLocation('prev')}>
              <FiChevronLeft />
            </Button>
            <Button size="sm" variant="outline" onClick={() => cycleLocation('next')}>
              <FiChevronRight />
            </Button>
          </div>
        </div>
      </Card>
      
      {/* Map Display */}
      <Card>
        <div className="h-[400px] mb-4">
          {mapDetails.viewingError ? (
            <div className="h-full bg-gray-100 flex items-center justify-center">
              <div className="text-center p-4">
                <FiMapPin className="text-red-500 mx-auto mb-2" size={32} />
                <p className="text-red-600 font-medium">Map Error Simulation</p>
                <p className="text-gray-800 text-sm mt-2">This is a simulated error state for testing purposes</p>
              </div>
            </div>
          ) : (
            <StaticMap 
              latitude={coordinates.latitude} 
              longitude={coordinates.longitude}
              title={PREDEFINED_LOCATIONS[currentLocationIndex].name}
              className="w-full h-full"
            />
          )}
        </div>
        
        <div className="flex flex-wrap gap-2">
          <Button onClick={useMyLocation} disabled={!userLocation}>
            <FiCrosshair className="mr-2" /> Use My Location
          </Button>
          
          <Button onClick={testMapLoadTime} variant="outline">
            Test Load Time
          </Button>
          
          <Button onClick={simulateMapError} variant="outline" className="text-red-600 border-red-600 hover:bg-red-50">
            Simulate Error
          </Button>
        </div>
        
        {mapDetails.loadTime && (
          <div className="mt-4 p-3 bg-gray-50 rounded-md">
            <p className="text-sm text-gray-900">
              <span className="font-medium">Last load time:</span> {mapDetails.loadTime.toFixed(2)}ms
            </p>
          </div>
        )}
      </Card>
      
      {/* Map Navigation Test */}
      <Card>
        <h2 className="text-xl font-semibold mb-4 text-black">Navigation Testing</h2>
        <p className="text-sm text-gray-900 mb-4">
          Test external mapping services for directions and location viewing
        </p>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <a 
            href={`https://www.google.com/maps?q=${coordinates.latitude},${coordinates.longitude}`}
            target="_blank" 
            rel="noopener noreferrer"
            className="block"
          >
            <Button variant="outline" className="w-full flex items-center">
              <FiMapPin className="mr-2" /> Open in Google Maps
            </Button>
          </a>
          
          <a 
            href={`https://www.google.com/maps/dir/?api=1&destination=${coordinates.latitude},${coordinates.longitude}`}
            target="_blank" 
            rel="noopener noreferrer"
            className="block"
          >
            <Button variant="outline" className="w-full flex items-center">
              <FiNavigation className="mr-2" /> Get Directions
            </Button>
          </a>
          
          {userLocation && (
            <a 
              href={`https://www.google.com/maps/dir/?api=1&origin=${userLocation.latitude},${userLocation.longitude}&destination=${coordinates.latitude},${coordinates.longitude}`}
              target="_blank" 
              rel="noopener noreferrer"
              className="block sm:col-span-2"
            >
              <Button className="w-full flex items-center">
                <FiNavigation className="mr-2" /> Directions from My Location
              </Button>
            </a>
          )}
        </div>
      </Card>
      
      {/* Location Presets */}
      <Card>
        <h2 className="text-xl font-semibold mb-4 text-black">Location Presets</h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-3">
          {PREDEFINED_LOCATIONS.map((location, index) => (
            <Button 
              key={location.name}
              variant={index === currentLocationIndex ? "filled" : "outline"}
              className={index === currentLocationIndex ? "bg-orange-500 text-white" : ""}
              onClick={() => {
                setCurrentLocationIndex(index);
                setCoordinates({
                  latitude: location.latitude,
                  longitude: location.longitude
                });
              }}
            >
              {location.name}
            </Button>
          ))}
        </div>
      </Card>
      
      <div className="text-center text-sm text-black pt-8">
        <p>Map Component Test</p>
        <p>Testing framework for HawkerRoute location features</p>
      </div>
    </div>
  );
} 