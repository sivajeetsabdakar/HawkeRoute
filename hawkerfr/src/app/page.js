"use client";
import Link from "next/link";
import Image from "next/image";
import Button from "@/components/ui/Button";
import { FiSearch, FiMapPin, FiClock, FiTruck } from "react-icons/fi";

export default function Home() {
  return (
    <div className="space-y-16">
      {/* Hero Section */}
      <section className="relative -mx-4 sm:-mx-6 md:-mx-8 lg:-mx-16 xl:-mx-24 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-r from-black to-transparent z-10"></div>
        <div className="relative w-full h-[500px]">
          <Image
            src="/images/hero-food.jpg"
            alt="Street food vendor"
            fill
            priority
            className="object-cover"
          />
        </div>
        <div className="absolute inset-0 z-20 flex items-center">
          <div className="container mx-auto px-4">
            <div className="max-w-xl">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-4">
                Connecting You to Street Food Vendors
              </h1>
              <p className="text-lg md:text-xl text-white mb-8">
                Order street food directly from hawkers and get it delivered to
                your doorstep.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link href="/hawkers">
                  <Button size="lg" leftIcon={<FiSearch />}>
                    Find Hawkers
                  </Button>
                </Link>
                <Link href="/register">
                  <Button
                    size="lg"
                    variant="outline"
                    className="bg-white bg-opacity-20"
                  >
                    Register as Hawker
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12">
          How HawkeRoute Works
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center p-6 rounded-lg shadow-md bg-white">
            <div className="mx-auto w-16 h-16 flex items-center justify-center rounded-full bg-orange-100 text-orange-600 mb-4">
              <FiSearch size={24} />
            </div>
            <h3 className="text-xl font-semibold mb-3">Discover Hawkers</h3>
            <p className="text-gray-600">
              Find street food vendors near you with our easy-to-use search
              feature.
            </p>
          </div>

          <div className="text-center p-6 rounded-lg shadow-md bg-white">
            <div className="mx-auto w-16 h-16 flex items-center justify-center rounded-full bg-orange-100 text-orange-600 mb-4">
              <FiMapPin size={24} />
            </div>
            <h3 className="text-xl font-semibold mb-3">Order Food</h3>
            <p className="text-gray-600">
              Browse menus, select your favorite dishes, and place your order in
              minutes.
            </p>
          </div>

          <div className="text-center p-6 rounded-lg shadow-md bg-white">
            <div className="mx-auto w-16 h-16 flex items-center justify-center rounded-full bg-orange-100 text-orange-600 mb-4">
              <FiTruck size={24} />
            </div>
            <h3 className="text-xl font-semibold mb-3">Get Delivery</h3>
            <p className="text-gray-600">
              Track your order in real-time and enjoy fresh street food at your
              doorstep.
            </p>
          </div>
        </div>
      </section>

      {/* For Hawkers Section */}
      <section className="bg-gray-100 py-16 -mx-4 sm:-mx-6 md:-mx-8 lg:-mx-16 xl:-mx-24">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center gap-8">
            <div className="md:w-1/2">
              <h2 className="text-3xl font-bold mb-4">Are You a Hawker?</h2>
              <p className="text-lg text-gray-600 mb-6">
                Join our platform to reach more customers, manage orders
                efficiently, and optimize your delivery routes.
              </p>
              <ul className="space-y-3 mb-8">
                <li className="flex items-center text-gray-600">
                  <span className="mr-2 text-green-500">✓</span>
                  <span>List your products and manage inventory</span>
                </li>
                <li className="flex items-center text-gray-600">
                  <span className="mr-2 text-green-500">✓</span>
                  <span>Receive orders and track deliveries</span>
                </li>
                <li className="flex items-center text-gray-600">
                  <span className="mr-2 text-green-500">✓</span>
                  <span>Get optimized delivery routes</span>
                </li>
                <li className="flex items-center text-gray-600">
                  <span className="mr-2 text-green-500">✓</span>
                  <span>Increase your customer base</span>
                </li>
              </ul>
              <Link href="/register">
                <Button size="lg">Register as Hawker</Button>
              </Link>
            </div>
            <div className="md:w-1/2 relative h-[400px]">
              <Image
                src="/images/hawker-vendor.jpg"
                alt="Hawker vendor"
                fill
                className="object-cover rounded-lg"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="container mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12">
          What Our Users Say
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 rounded-full bg-gray-200 mr-4"></div>
              <div>
                <h4 className="font-semibold">Sarah Lee</h4>
                <p className="text-sm text-gray-600">Customer</p>
              </div>
            </div>
            <p className="text-gray-600">
              I love being able to order from my favorite street food vendors
              without having to travel. The delivery is always prompt and the
              food is fresh!
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 rounded-full bg-gray-200 mr-4"></div>
              <div>
                <h4 className="font-semibold">Ahmad Khan</h4>
                <p className="text-sm text-gray-600">Hawker</p>
              </div>
            </div>
            <p className="text-gray-600">
              Since joining HawkeRoute, my business has grown by 40%. The route
              optimization helps me deliver more orders efficiently.
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow-md">
            <div className="flex items-center mb-4">
              <div className="w-12 h-12 rounded-full bg-gray-200 mr-4"></div>
              <div>
                <h4 className="font-semibold">Mei Lin</h4>
                <p className="text-sm text-gray-600">Customer</p>
              </div>
            </div>
            <p className="text-gray-600">
              HawkeRoute has made it so easy to discover new hawkers in my area.
              I&apos;ve found some amazing food that I wouldn&apos;t have known
              about otherwise!
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="bg-orange-600 py-16 -mx-4 sm:-mx-6 md:-mx-8 lg:-mx-16 xl:-mx-24">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-6">
            Ready to Order Delicious Street Food?
          </h2>
          <p className="text-xl text-white mb-8 max-w-2xl mx-auto">
            Join thousands of satisfied customers who enjoy street food
            delivered to their doorstep.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/hawkers">
              <Button
                size="lg"
                className="bg-white text-orange-600 hover:bg-gray-100"
              >
                Browse Hawkers
              </Button>
            </Link>
            <Link href="/register">
              <Button
                size="lg"
                variant="outline"
                className="border-white text-white hover:bg-orange-700"
              >
                Create Account
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
}
