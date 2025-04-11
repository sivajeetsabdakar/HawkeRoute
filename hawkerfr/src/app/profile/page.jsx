"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { useAuth } from "@/contexts/AuthContext";
import { useForm } from "react-hook-form";
import {
  FiUser,
  FiMail,
  FiPhone,
  FiMapPin,
  FiLock,
  FiSave,
  FiCamera,
} from "react-icons/fi";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Card from "@/components/ui/Card";
import { authAPI } from "@/lib/api";
import { getErrorMessage } from "@/lib/utils";

export default function ProfilePage() {
  const router = useRouter();
  const { user, isAuthenticated, isHawker } = useAuth();
  const [activeTab, setActiveTab] = useState("personal");
  const [updating, setUpdating] = useState(false);
  const [passwordUpdating, setPasswordUpdating] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm({
    defaultValues: {
      name: user?.name || "",
      email: user?.email || "",
      phone: user?.phone || "",
      business_name: user?.business_name || "",
      business_address: user?.business_address || "",
      latitude: user?.latitude || "",
      longitude: user?.longitude || "",
    },
  });

  const {
    register: registerPassword,
    handleSubmit: handlePasswordSubmit,
    formState: { errors: passwordErrors },
    watch,
  } = useForm({
    defaultValues: {
      current_password: "",
      new_password: "",
      confirm_password: "",
    },
  });

  const newPassword = watch("new_password", "");

  const onSubmit = async (data) => {
    try {
      setUpdating(true);
      setError("");
      setSuccess("");

      // In a real app, this would update the user profile
      // For now, let's just simulate a successful update
      await new Promise((resolve) => setTimeout(resolve, 1000));

      setSuccess("Profile updated successfully");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setUpdating(false);
    }
  };

  const onPasswordSubmit = async (data) => {
    try {
      setPasswordUpdating(true);
      setError("");
      setSuccess("");

      // In a real app, this would update the password
      // For now, let's just simulate a successful update
      await new Promise((resolve) => setTimeout(resolve, 1000));

      setSuccess("Password updated successfully");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setPasswordUpdating(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold mb-4">
          You need to login to view your profile
        </h1>
        <Button onClick={() => router.push("/login?redirect=/profile")}>
          Login
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto">
      <h1 className="text-3xl font-bold mb-8">My Profile</h1>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        {/* Sidebar */}
        <div className="md:col-span-1">
          <Card className="p-0 overflow-hidden">
            <div className="bg-gradient-to-r from-orange-500 to-orange-600 py-6 px-4 text-white">
              <div className="relative w-20 h-20 mx-auto rounded-full overflow-hidden mb-4 bg-white">
                <Image
                  src="/images/user-placeholder.jpg"
                  alt={user?.name || "User"}
                  fill
                  className="object-cover"
                />
                <button className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity">
                  <FiCamera size={24} className="text-white" />
                </button>
              </div>
              <h2 className="text-center font-semibold text-lg">
                {user?.name}
              </h2>
              <p className="text-center text-sm text-orange-100">
                {user?.role}
              </p>
            </div>

            <div className="p-0">
              <button
                className={`w-full text-left px-4 py-3 border-l-4 ${
                  activeTab === "personal"
                    ? "border-orange-600 bg-orange-50 text-orange-600"
                    : "border-transparent hover:bg-gray-50"
                }`}
                onClick={() => setActiveTab("personal")}
              >
                Personal Information
              </button>

              {isHawker && (
                <button
                  className={`w-full text-left px-4 py-3 border-l-4 ${
                    activeTab === "business"
                      ? "border-orange-600 bg-orange-50 text-orange-600"
                      : "border-transparent hover:bg-gray-50"
                  }`}
                  onClick={() => setActiveTab("business")}
                >
                  Business Information
                </button>
              )}

              <button
                className={`w-full text-left px-4 py-3 border-l-4 ${
                  activeTab === "security"
                    ? "border-orange-600 bg-orange-50 text-orange-600"
                    : "border-transparent hover:bg-gray-50"
                }`}
                onClick={() => setActiveTab("security")}
              >
                Security
              </button>
            </div>
          </Card>
        </div>

        {/* Main Content */}
        <div className="md:col-span-3">
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded mb-6">
              {error}
            </div>
          )}

          {success && (
            <div className="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded mb-6">
              {success}
            </div>
          )}

          {activeTab === "personal" && (
            <Card title="Personal Information">
              <form onSubmit={handleSubmit(onSubmit)}>
                <div className="space-y-6">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div className="flex items-start">
                      <FiUser className="mt-2.5 mr-2 text-gray-400" />
                      <Input
                        label="Full Name"
                        id="name"
                        error={errors.name?.message}
                        containerClassName="flex-grow"
                        {...register("name", {
                          required: "Name is required",
                        })}
                      />
                    </div>

                    <div className="flex items-start">
                      <FiMail className="mt-2.5 mr-2 text-gray-400" />
                      <Input
                        label="Email"
                        type="email"
                        id="email"
                        error={errors.email?.message}
                        containerClassName="flex-grow"
                        {...register("email", {
                          required: "Email is required",
                          pattern: {
                            value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
                            message: "Please enter a valid email",
                          },
                        })}
                      />
                    </div>
                  </div>

                  <div className="flex items-start">
                    <FiPhone className="mt-2.5 mr-2 text-gray-400" />
                    <Input
                      label="Phone Number"
                      id="phone"
                      error={errors.phone?.message}
                      containerClassName="flex-grow"
                      {...register("phone", {
                        required: "Phone number is required",
                        pattern: {
                          value: /^\d{10}$/,
                          message: "Please enter a valid 10-digit phone number",
                        },
                      })}
                    />
                  </div>
                </div>

                <div className="mt-6 flex justify-end">
                  <Button
                    type="submit"
                    isLoading={updating}
                    leftIcon={<FiSave />}
                  >
                    Save Changes
                  </Button>
                </div>
              </form>
            </Card>
          )}

          {activeTab === "business" && isHawker && (
            <Card title="Business Information">
              <form onSubmit={handleSubmit(onSubmit)}>
                <div className="space-y-6">
                  <div className="flex items-start">
                    <FiUser className="mt-2.5 mr-2 text-gray-400" />
                    <Input
                      label="Business Name"
                      id="business_name"
                      error={errors.business_name?.message}
                      containerClassName="flex-grow"
                      {...register("business_name", {
                        required: "Business name is required",
                      })}
                    />
                  </div>

                  <div className="flex items-start">
                    <FiMapPin className="mt-2.5 mr-2 text-gray-400" />
                    <Input
                      label="Business Address"
                      id="business_address"
                      error={errors.business_address?.message}
                      containerClassName="flex-grow"
                      {...register("business_address", {
                        required: "Business address is required",
                      })}
                    />
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <Input
                      label="Latitude"
                      id="latitude"
                      error={errors.latitude?.message}
                      {...register("latitude", {
                        required: "Latitude is required",
                        pattern: {
                          value: /^-?\d+(\.\d+)?$/,
                          message: "Please enter a valid latitude",
                        },
                      })}
                    />

                    <Input
                      label="Longitude"
                      id="longitude"
                      error={errors.longitude?.message}
                      {...register("longitude", {
                        required: "Longitude is required",
                        pattern: {
                          value: /^-?\d+(\.\d+)?$/,
                          message: "Please enter a valid longitude",
                        },
                      })}
                    />
                  </div>
                </div>

                <div className="mt-6 flex justify-end">
                  <Button
                    type="submit"
                    isLoading={updating}
                    leftIcon={<FiSave />}
                  >
                    Save Changes
                  </Button>
                </div>
              </form>
            </Card>
          )}

          {activeTab === "security" && (
            <Card title="Security">
              <form onSubmit={handlePasswordSubmit(onPasswordSubmit)}>
                <div className="space-y-6">
                  <div className="flex items-start">
                    <FiLock className="mt-2.5 mr-2 text-gray-400" />
                    <Input
                      label="Current Password"
                      type="password"
                      id="current_password"
                      error={passwordErrors.current_password?.message}
                      containerClassName="flex-grow"
                      {...registerPassword("current_password", {
                        required: "Current password is required",
                      })}
                    />
                  </div>

                  <div className="flex items-start">
                    <FiLock className="mt-2.5 mr-2 text-gray-400" />
                    <Input
                      label="New Password"
                      type="password"
                      id="new_password"
                      error={passwordErrors.new_password?.message}
                      containerClassName="flex-grow"
                      {...registerPassword("new_password", {
                        required: "New password is required",
                        minLength: {
                          value: 6,
                          message: "Password must be at least 6 characters",
                        },
                      })}
                    />
                  </div>

                  <div className="flex items-start">
                    <FiLock className="mt-2.5 mr-2 text-gray-400" />
                    <Input
                      label="Confirm New Password"
                      type="password"
                      id="confirm_password"
                      error={passwordErrors.confirm_password?.message}
                      containerClassName="flex-grow"
                      {...registerPassword("confirm_password", {
                        required: "Please confirm your new password",
                        validate: (value) =>
                          value === newPassword || "The passwords do not match",
                      })}
                    />
                  </div>
                </div>

                <div className="mt-6 flex justify-end">
                  <Button
                    type="submit"
                    isLoading={passwordUpdating}
                    leftIcon={<FiSave />}
                  >
                    Update Password
                  </Button>
                </div>
              </form>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
