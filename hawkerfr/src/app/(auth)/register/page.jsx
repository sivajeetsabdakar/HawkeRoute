"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { useAuth } from "@/contexts/AuthContext";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Card from "@/components/ui/Card";
import { getErrorMessage } from "@/lib/utils";

export default function RegisterPage() {
  const router = useRouter();
  const { register: registerUser } = useAuth();
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [userType, setUserType] = useState("customer");

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors },
  } = useForm({
    defaultValues: {
      name: "",
      email: "",
      phone: "",
      password: "",
      confirmPassword: "",
      role: "customer",
      business_name: "",
      business_address: "",
      latitude: "",
      longitude: "",
    },
  });

  const password = watch("password");

  const onSubmit = async (data) => {
    try {
      setIsLoading(true);
      setError("");

      // Remove confirmPassword as it's not needed for API
      const { confirmPassword, ...registerData } = data;

      // Parse latitude and longitude if provided
      if (registerData.latitude) {
        registerData.latitude = parseFloat(registerData.latitude);
      }

      if (registerData.longitude) {
        registerData.longitude = parseFloat(registerData.longitude);
      }

      await registerUser(registerData);
      router.push("/");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setIsLoading(false);
    }
  };

  const toggleUserType = (type) => {
    setUserType(type);
  };

  return (
    <div className="flex justify-center items-center py-8">
      <Card className="w-full max-w-2xl">
        <div className="text-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">
            Create an Account
          </h1>
          <p className="text-gray-600 mt-2">
            Join HawkeRoute to order from or sell street food
          </p>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        <div className="flex border-b mb-6">
          <button
            type="button"
            className={`flex-1 py-2 font-medium text-center ${
              userType === "customer"
                ? "text-orange-600 border-b-2 border-orange-600"
                : "text-gray-500 hover:text-gray-700"
            }`}
            onClick={() => toggleUserType("customer")}
          >
            Register as Customer
          </button>
          <button
            type="button"
            className={`flex-1 py-2 font-medium text-center ${
              userType === "hawker"
                ? "text-orange-600 border-b-2 border-orange-600"
                : "text-gray-500 hover:text-gray-700"
            }`}
            onClick={() => toggleUserType("hawker")}
          >
            Register as Hawker
          </button>
        </div>

        <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
          <input type="hidden" {...register("role")} value={userType} />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Full Name"
              id="name"
              placeholder="John Doe"
              error={errors.name?.message}
              {...register("name", {
                required: "Name is required",
              })}
            />

            <Input
              label="Email"
              type="email"
              id="email"
              placeholder="your@email.com"
              error={errors.email?.message}
              {...register("email", {
                required: "Email is required",
                pattern: {
                  value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                  message: "Please enter a valid email",
                },
              })}
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <Input
              label="Phone Number"
              id="phone"
              placeholder="1234567890"
              error={errors.phone?.message}
              {...register("phone", {
                required: "Phone number is required",
                pattern: {
                  value: /^\d{10}$/,
                  message: "Please enter a valid 10-digit phone number",
                },
              })}
            />

            <Input
              label="Password"
              type="password"
              id="password"
              placeholder="••••••••"
              error={errors.password?.message}
              {...register("password", {
                required: "Password is required",
                minLength: {
                  value: 6,
                  message: "Password must be at least 6 characters",
                },
              })}
            />
          </div>

          <Input
            label="Confirm Password"
            type="password"
            id="confirmPassword"
            placeholder="••••••••"
            error={errors.confirmPassword?.message}
            {...register("confirmPassword", {
              required: "Please confirm your password",
              validate: (value) =>
                value === password || "The passwords do not match",
            })}
          />

          {userType === "hawker" && (
            <div className="border-t border-gray-200 pt-4 mt-6">
              <h3 className="text-lg font-medium mb-4">
                Hawker Business Details
              </h3>

              <div className="space-y-4">
                <Input
                  label="Business Name"
                  id="business_name"
                  placeholder="Your Street Food Business"
                  error={errors.business_name?.message}
                  {...register("business_name", {
                    required:
                      userType === "hawker"
                        ? "Business name is required"
                        : false,
                  })}
                />

                <Input
                  label="Business Address"
                  id="business_address"
                  placeholder="123 Street Name, City"
                  error={errors.business_address?.message}
                  {...register("business_address", {
                    required:
                      userType === "hawker"
                        ? "Business address is required"
                        : false,
                  })}
                />

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <Input
                    label="Latitude"
                    id="latitude"
                    placeholder="1.2345"
                    error={errors.latitude?.message}
                    {...register("latitude", {
                      required:
                        userType === "hawker" ? "Latitude is required" : false,
                      pattern: {
                        value: /^-?\d+(\.\d+)?$/,
                        message: "Please enter a valid latitude",
                      },
                    })}
                  />

                  <Input
                    label="Longitude"
                    id="longitude"
                    placeholder="6.7890"
                    error={errors.longitude?.message}
                    {...register("longitude", {
                      required:
                        userType === "hawker" ? "Longitude is required" : false,
                      pattern: {
                        value: /^-?\d+(\.\d+)?$/,
                        message: "Please enter a valid longitude",
                      },
                    })}
                  />
                </div>
              </div>
            </div>
          )}

          <div className="pt-4">
            <Button type="submit" fullWidth isLoading={isLoading}>
              Create Account
            </Button>
          </div>
        </form>

        <div className="mt-6 text-center">
          <p className="text-sm text-gray-600">
            Already have an account?{" "}
            <Link
              href="/login"
              className="text-orange-600 hover:text-orange-500 font-medium"
            >
              Sign in
            </Link>
          </p>
        </div>
      </Card>
    </div>
  );
}
