/** @type {import('next').NextConfig} */
const nextConfig = {
  images: {
    domains: ["example.com", "res.cloudinary.com"],
    remotePatterns: [
      {
        protocol: "https",
        hostname: "example.com",
      },
      {
        protocol: "https",
        hostname: "res.cloudinary.com",
      },
    ],
  },
};

export default nextConfig;
