import { io } from "socket.io-client";

let socket;

export const initializeSocket = () => {
  if (!socket) {
    socket = io("wss://api.hawkeroute.com/delivery", {
      transports: ["websocket"],
      autoConnect: false,
    });
  }

  // Connect to the server
  if (!socket.connected) {
    socket.connect();
  }

  return socket;
};

export const joinTrackingRoom = (hawkerId) => {
  const socket = initializeSocket();
  socket.emit("join_tracking", { hawker_id: hawkerId });
};

export const leaveTrackingRoom = (hawkerId) => {
  const socket = initializeSocket();
  socket.emit("leave_tracking", { hawker_id: hawkerId });
};

export const onLocationUpdate = (callback) => {
  const socket = initializeSocket();
  socket.on("location_update", callback);

  // Return unsubscribe function
  return () => {
    socket.off("location_update", callback);
  };
};

export const closeSocket = () => {
  if (socket) {
    socket.disconnect();
  }
};

export default {
  initializeSocket,
  joinTrackingRoom,
  leaveTrackingRoom,
  onLocationUpdate,
  closeSocket,
};
