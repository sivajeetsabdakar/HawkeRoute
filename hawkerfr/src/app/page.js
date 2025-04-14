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
          <img
            src="https://media.istockphoto.com/id/182766047/photo/indian-banana-seller.jpg?s=2048x2048&w=is&k=20&c=0X_jEsRYTcOwfY9TLLVNs6h7dU41z_tJLj4jj_LpnrQ="
            alt="Hawker"
            class="w-full h-200 object-cover"
          />
        </div>
        <div className="absolute inset-0 z-20 flex items-center">
          <div className="container mx-auto px-4">
            <div className="max-w-xl">
              <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold text-white mb-4">
                Connecting You to Hawkers
              </h1>
              <p className="text-lg md:text-xl text-white mb-8">
                Order any product or services directly from hawkers and get it
                delivered to your doorstep.
              </p>
              <div className="flex flex-col sm:flex-row gap-4">
                <Link href="/hawkers">
                  <Button size="lg" leftIcon={<FiSearch />}>
                    Find Hawkers
                  </Button>
                </Link>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto">
        <h2 className="text-3xl font-bold text-center mb-12 text-white">
          How HawkeRoute Works
        </h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="text-center p-6 rounded-lg shadow-md bg-white">
            <div className="mx-auto w-16 h-16 flex items-center justify-center rounded-full bg-orange-100 text-orange-600 mb-4">
              <FiSearch size={24} />
            </div>
            <h3 className="text-xl font-semibold mb-3 text-black">
              Discover Hawkers
            </h3>
            <p className="text-gray-600">
              Find hawkers near you with our easy-to-use search feature.
            </p>
          </div>

          <div className="text-center p-6 rounded-lg shadow-md bg-white">
            <div className="mx-auto w-16 h-16 flex items-center justify-center rounded-full bg-orange-100 text-orange-600 mb-4">
              <FiMapPin size={24} />
            </div>
            <h3 className="text-xl font-semibold mb-3 text-black">
              Order Products or Services
            </h3>
            <p className="text-gray-600">
              Browse menus, select your favorite dishes, and place your order in
              minutes.
            </p>
          </div>

          <div className="text-center p-6 rounded-lg shadow-md bg-white">
            <div className="mx-auto w-16 h-16 flex items-center justify-center rounded-full bg-orange-100 text-orange-600 mb-4">
              <FiTruck size={24} />
            </div>
            <h3 className="text-xl font-semibold mb-3 text-black ">
              Get Delivery
            </h3>
            <p className="text-gray-600">
              Track your order in real-time and enjoy fresh products or services
              at your doorstep.
            </p>
          </div>
        </div>
      </section>

      {/* For Hawkers Section */}

      {/* Testimonials Section */}

      {/* CTA Section */}
      <section className="bg-orange-600 py-16 -mx-4 sm:-mx-6 md:-mx-8 lg:-mx-16 xl:-mx-24">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold text-white mb-6">
            Ready to Order any Product or Service?
          </h2>
          <p className="text-xl text-white mb-8 max-w-2xl mx-auto">
            Join thousands of satisfied customers who enjoy our services.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/hawkers">
              <Button
                size="lg"
                variant="outline"
                className="border-white text-white hover:bg-orange-700"
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
