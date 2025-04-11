"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { useForm } from "react-hook-form";
import Image from "next/image";
import Link from "next/link";
import { FiSave, FiArrowLeft, FiTrash } from "react-icons/fi";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { useAuth } from "@/contexts/AuthContext";
import { productsAPI } from "@/lib/api";
import { getErrorMessage } from "@/lib/utils";

export default function EditProductPage({ params }) {
  const productId = params.id;
  const router = useRouter();
  const { isAuthenticated, isHawker } = useAuth();

  const [loading, setLoading] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [product, setProduct] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);

  const {
    register,
    handleSubmit,
    formState: { errors },
    setValue,
    watch,
  } = useForm();

  // Watch form values for image preview and validation
  const watchImage = watch("image");

  useEffect(() => {
    async function loadProduct() {
      try {
        setLoading(true);
        setError("");

        const productData = await productsAPI.getProduct(productId);

        // Make sure the product belongs to this hawker
        if (!productData.owned_by_current_hawker) {
          router.push("/products/manage");
          return;
        }

        setProduct(productData);
        setImagePreview(productData.image_url);

        // Set form values
        setValue("name", productData.name);
        setValue("description", productData.description);
        setValue("price", productData.price);
        setValue("category", productData.category);
        setValue("is_available", productData.is_available);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    }

    if (isAuthenticated && isHawker) {
      loadProduct();
    }
  }, [isAuthenticated, isHawker, productId, router, setValue]);

  // Handle image preview when a file is selected
  useEffect(() => {
    if (watchImage && watchImage[0]) {
      const file = watchImage[0];
      const reader = new FileReader();
      reader.onloadend = () => {
        setImagePreview(reader.result);
      };
      reader.readAsDataURL(file);
    }
  }, [watchImage]);

  const onSubmit = async (data) => {
    try {
      setSubmitting(true);
      setError("");

      // Create a new FormData object to handle file upload
      const formData = new FormData();
      formData.append("name", data.name);
      formData.append("description", data.description);
      formData.append("price", data.price);
      formData.append("category", data.category);
      formData.append("is_available", data.is_available);

      // Only append image if a new one was selected
      if (data.image && data.image[0]) {
        formData.append("image", data.image[0]);
      }

      await productsAPI.updateProduct(productId, formData);

      // Redirect to the manage products page with success message
      router.push("/products/manage?success=Product updated successfully");
    } catch (err) {
      setError(getErrorMessage(err));
      window.scrollTo(0, 0); // Scroll to top to show error message
    } finally {
      setSubmitting(false);
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold mb-4">
          You need to login to edit products
        </h1>
        <Button
          onClick={() =>
            router.push(`/login?redirect=/products/edit/${productId}`)
          }
        >
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
          You need a hawker account to edit products.
        </p>
        <Button onClick={() => router.push("/")}>Go Home</Button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="text-center py-12">
        <div className="w-12 h-12 border-4 border-gray-200 border-t-orange-500 rounded-full animate-spin mx-auto mb-4"></div>
        <p>Loading product information...</p>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold mb-4">Product not found</h1>
        <p className="text-gray-600 mb-6">
          The product you're trying to edit could not be found.
        </p>
        <Button onClick={() => router.push("/products/manage")}>
          Back to Products
        </Button>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="flex items-center mb-8">
        <Link href="/products/manage">
          <Button variant="ghost" leftIcon={<FiArrowLeft />}>
            Back to Products
          </Button>
        </Link>
        <h1 className="text-3xl font-bold ml-4">Edit Product</h1>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      <Card className="overflow-hidden">
        <form onSubmit={handleSubmit(onSubmit)}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-6">
            <div className="md:col-span-2">
              <h2 className="text-xl font-semibold mb-4">Product Details</h2>
            </div>

            {/* Left Column - Form Fields */}
            <div className="space-y-6">
              <div>
                <label
                  htmlFor="name"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Product Name*
                </label>
                <input
                  id="name"
                  type="text"
                  className={`w-full px-4 py-2 border rounded-lg ${
                    errors.name ? "border-red-500" : "border-gray-300"
                  }`}
                  placeholder="Enter product name"
                  {...register("name", {
                    required: "Product name is required",
                  })}
                />
                {errors.name && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.name.message}
                  </p>
                )}
              </div>

              <div>
                <label
                  htmlFor="description"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Description*
                </label>
                <textarea
                  id="description"
                  rows="4"
                  className={`w-full px-4 py-2 border rounded-lg ${
                    errors.description ? "border-red-500" : "border-gray-300"
                  }`}
                  placeholder="Describe your product"
                  {...register("description", {
                    required: "Description is required",
                  })}
                />
                {errors.description && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.description.message}
                  </p>
                )}
              </div>

              <div>
                <label
                  htmlFor="price"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Price ($)*
                </label>
                <input
                  id="price"
                  type="number"
                  step="0.01"
                  className={`w-full px-4 py-2 border rounded-lg ${
                    errors.price ? "border-red-500" : "border-gray-300"
                  }`}
                  placeholder="0.00"
                  {...register("price", {
                    required: "Price is required",
                    min: {
                      value: 0.01,
                      message: "Price must be greater than 0",
                    },
                    pattern: {
                      value: /^\d+(\.\d{1,2})?$/,
                      message: "Please enter a valid price",
                    },
                  })}
                />
                {errors.price && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.price.message}
                  </p>
                )}
              </div>

              <div>
                <label
                  htmlFor="category"
                  className="block text-sm font-medium text-gray-700 mb-1"
                >
                  Category
                </label>
                <select
                  id="category"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg"
                  {...register("category")}
                >
                  <option value="">Select a category</option>
                  <option value="Main Dish">Main Dish</option>
                  <option value="Side Dish">Side Dish</option>
                  <option value="Dessert">Dessert</option>
                  <option value="Beverage">Beverage</option>
                  <option value="Snack">Snack</option>
                  <option value="Special">Special</option>
                </select>
              </div>

              <div className="flex items-center">
                <input
                  id="is_available"
                  type="checkbox"
                  className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
                  {...register("is_available")}
                />
                <label
                  htmlFor="is_available"
                  className="ml-2 block text-sm text-gray-700"
                >
                  Available for order
                </label>
              </div>
            </div>

            {/* Right Column - Image Upload */}
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Product Image
                </label>
                <div className="mt-1 flex flex-col items-center">
                  <div className="relative w-full h-48 mb-4 border rounded-lg overflow-hidden bg-gray-100">
                    {imagePreview ? (
                      <Image
                        src={imagePreview}
                        alt="Product preview"
                        fill
                        className="object-cover"
                      />
                    ) : (
                      <div className="flex items-center justify-center h-full">
                        <p className="text-gray-500">No image selected</p>
                      </div>
                    )}
                  </div>

                  <div className="flex items-center justify-center w-full">
                    <label className="w-full flex flex-col items-center px-4 py-2 bg-white text-orange-500 rounded-lg border border-orange-500 cursor-pointer hover:bg-orange-50">
                      <span className="text-base">Select a new image</span>
                      <input
                        type="file"
                        className="hidden"
                        accept="image/*"
                        {...register("image")}
                      />
                    </label>
                  </div>

                  {imagePreview && watchImage && watchImage[0] && (
                    <button
                      type="button"
                      className="mt-2 text-sm text-red-600 hover:text-red-800 flex items-center"
                      onClick={() => {
                        setValue("image", null);
                        setImagePreview(product.image_url);
                      }}
                    >
                      <FiTrash size={14} className="mr-1" />
                      Reset to original image
                    </button>
                  )}
                </div>
              </div>
            </div>
          </div>

          <div className="border-t border-gray-200 p-6 flex justify-end space-x-4">
            <Link href="/products/manage">
              <Button variant="ghost">Cancel</Button>
            </Link>
            <Button
              type="submit"
              leftIcon={<FiSave />}
              disabled={submitting}
              isLoading={submitting}
            >
              Save Changes
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
}
