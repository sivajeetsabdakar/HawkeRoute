"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { useForm } from "react-hook-form";
import {
  FiArrowLeft,
  FiSave,
  FiUpload,
  FiDollarSign,
  FiList,
} from "react-icons/fi";
import Button from "@/components/ui/Button";
import Input from "@/components/ui/Input";
import Card from "@/components/ui/Card";
import { useAuth } from "@/contexts/AuthContext";
import { productsAPI } from "@/lib/api";
import { getErrorMessage } from "@/lib/utils";

export default function AddProductPage() {
  const router = useRouter();
  const { isAuthenticated, isHawker } = useAuth();

  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [imagePreview, setImagePreview] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    reset,
  } = useForm({
    defaultValues: {
      name: "",
      description: "",
      price: "",
      is_available: true,
      category: "",
      image: null,
    },
  });

  // Watch the is_available value
  const isAvailable = watch("is_available");

  const onSubmit = async (data) => {
    try {
      setSubmitting(true);
      setError("");

      // In a real application, you would handle the image upload here
      // For this example, we'll just simulate a successful creation

      const formData = {
        name: data.name,
        description: data.description,
        price: parseFloat(data.price),
        is_available: data.is_available,
        category: data.category || null,
        image_url: "/images/placeholder-food.jpg", // Default placeholder image
      };

      // If we had a real image upload
      // if (data.image && data.image[0]) {
      //   const imageUrl = await uploadImage(data.image[0]);
      //   formData.image_url = imageUrl;
      // }

      await productsAPI.createProduct(formData);

      // Reset the form
      reset();
      setImagePreview("");

      // Show success and redirect
      router.push("/products/manage?success=Product created successfully");
    } catch (err) {
      setError(getErrorMessage(err));
    } finally {
      setSubmitting(false);
    }
  };

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      // Create a preview URL for the selected image
      const previewUrl = URL.createObjectURL(file);
      setImagePreview(previewUrl);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold mb-4">
          You need to login to add products
        </h1>
        <Button onClick={() => router.push("/login?redirect=/products/add")}>
          Login
        </Button>
      </div>
    );
  }

  if (!isHawker) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold mb-4">
          Only hawkers can access this page
        </h1>
        <p className="text-gray-600 mb-6">
          You need a hawker account to add products.
        </p>
        <Button onClick={() => router.push("/")}>Go Home</Button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center mb-8">
        <button
          onClick={() => router.back()}
          className="mr-4 text-gray-600 hover:text-gray-900 flex items-center"
        >
          <FiArrowLeft className="mr-1" />
          <span>Back</span>
        </button>
        <h1 className="text-3xl font-bold">Add New Product</h1>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      <Card>
        <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <div className="mb-6">
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Product Image
                </label>
                <div className="relative mt-2 flex justify-center border-2 border-dashed border-gray-300 rounded-lg p-6">
                  {imagePreview ? (
                    <div className="relative w-full h-48">
                      <Image
                        src={imagePreview}
                        alt="Product image preview"
                        fill
                        className="object-contain"
                      />
                      <button
                        type="button"
                        className="absolute inset-0 bg-black bg-opacity-50 flex items-center justify-center opacity-0 hover:opacity-100 transition-opacity"
                        onClick={() => document.getElementById("image").click()}
                      >
                        <FiUpload size={24} className="text-white" />
                      </button>
                    </div>
                  ) : (
                    <div className="text-center">
                      <FiUpload size={36} className="mx-auto text-gray-400" />
                      <p className="mt-2 text-sm text-gray-600">
                        Click or drag file to upload product image
                      </p>
                    </div>
                  )}
                  <input
                    id="image"
                    type="file"
                    accept="image/*"
                    className="hidden"
                    {...register("image")}
                    onChange={handleImageChange}
                  />
                </div>
              </div>

              <div className="flex items-center mb-6">
                <input
                  type="checkbox"
                  id="is_available"
                  className="h-4 w-4 text-orange-600 border-gray-300 rounded focus:ring-orange-500"
                  {...register("is_available")}
                />
                <label
                  htmlFor="is_available"
                  className="ml-2 block text-sm text-gray-700"
                >
                  Product is available for purchase
                </label>
              </div>
            </div>

            <div className="space-y-6">
              <div className="flex items-start">
                <FiList className="mt-2.5 mr-2 text-gray-400" />
                <Input
                  label="Product Name"
                  id="name"
                  placeholder="Enter product name"
                  error={errors.name?.message}
                  containerClassName="flex-grow"
                  {...register("name", {
                    required: "Product name is required",
                  })}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  id="description"
                  rows={4}
                  className="w-full rounded-md border-gray-300 shadow-sm focus:border-orange-500 focus:ring-orange-500"
                  placeholder="Enter product description"
                  {...register("description", {
                    required: "Description is required",
                  })}
                ></textarea>
                {errors.description && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.description.message}
                  </p>
                )}
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="flex items-start">
                  <FiDollarSign className="mt-2.5 mr-2 text-gray-400" />
                  <Input
                    label="Price"
                    id="price"
                    type="number"
                    step="0.01"
                    min="0"
                    placeholder="0.00"
                    error={errors.price?.message}
                    containerClassName="flex-grow"
                    {...register("price", {
                      required: "Price is required",
                      min: {
                        value: 0,
                        message: "Price must be greater than 0",
                      },
                    })}
                  />
                </div>

                <Input
                  label="Category (optional)"
                  id="category"
                  placeholder="e.g. Main Dish, Beverage"
                  error={errors.category?.message}
                  {...register("category")}
                />
              </div>
            </div>
          </div>

          <div className="flex justify-end space-x-4">
            <Link href="/products/manage">
              <Button variant="ghost">Cancel</Button>
            </Link>
            <Button type="submit" leftIcon={<FiSave />} isLoading={submitting}>
              Add Product
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
