"use client";

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import {
  FiPlus,
  FiEdit,
  FiTrash2,
  FiEye,
  FiCheckCircle,
  FiXCircle,
} from "react-icons/fi";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import { useAuth } from "@/contexts/AuthContext";
import { productsAPI } from "@/lib/api";
import { getErrorMessage } from "@/lib/utils";

export default function ManageProductsPage() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const { isAuthenticated, isHawker } = useAuth();

  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [successMessage, setSuccessMessage] = useState("");
  const [deleteModalOpen, setDeleteModalOpen] = useState(false);
  const [productToDelete, setProductToDelete] = useState(null);

  useEffect(() => {
    // Check if there's a success message in the URL
    const successMsg = searchParams.get("success");
    if (successMsg) {
      setSuccessMessage(successMsg);

      // Clear the success message after 5 seconds
      const timer = setTimeout(() => {
        setSuccessMessage("");
      }, 5000);

      return () => clearTimeout(timer);
    }
  }, [searchParams]);

  useEffect(() => {
    async function loadProducts() {
      try {
        setLoading(true);
        const data = await productsAPI.getHawkerProducts();
        setProducts(data);
      } catch (err) {
        setError(getErrorMessage(err));
      } finally {
        setLoading(false);
      }
    }

    if (isAuthenticated && isHawker) {
      loadProducts();
    }
  }, [isAuthenticated, isHawker]);

  const handleDeleteClick = (product) => {
    setProductToDelete(product);
    setDeleteModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!productToDelete) return;

    try {
      await productsAPI.deleteProduct(productToDelete.id);
      setProducts(products.filter((p) => p.id !== productToDelete.id));
      setSuccessMessage("Product deleted successfully");
      setDeleteModalOpen(false);
      setProductToDelete(null);
    } catch (err) {
      setError(getErrorMessage(err));
    }
  };

  if (!isAuthenticated) {
    return (
      <div className="text-center py-12">
        <h1 className="text-2xl font-bold mb-4">
          You need to login to manage products
        </h1>
        <Button onClick={() => router.push("/login?redirect=/products/manage")}>
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
          You need a hawker account to manage products.
        </p>
        <Button onClick={() => router.push("/")}>Go Home</Button>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold">Manage Products</h1>
        <Link href="/products/add">
          <Button leftIcon={<FiPlus />}>Add New Product</Button>
        </Link>
      </div>

      {successMessage && (
        <div className="bg-green-50 border border-green-200 text-green-600 px-4 py-3 rounded mb-6">
          {successMessage}
        </div>
      )}

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-600 px-4 py-3 rounded mb-6">
          {error}
        </div>
      )}

      {loading ? (
        <div className="text-center py-12">
          <div className="w-12 h-12 border-4 border-gray-200 border-t-orange-500 rounded-full animate-spin mx-auto mb-4"></div>
          <p>Loading products...</p>
        </div>
      ) : products.length === 0 ? (
        <Card className="text-center py-12">
          <h2 className="text-xl font-semibold mb-4">No products yet</h2>
          <p className="text-gray-600 mb-6">
            You haven't added any products to your menu.
          </p>
          <Link href="/products/add">
            <Button leftIcon={<FiPlus />}>Add Your First Product</Button>
          </Link>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map((product) => (
            <Card key={product.id} className="overflow-hidden">
              <div className="relative h-48 w-full">
                <Image
                  src={product.image_url || "/images/placeholder-food.jpg"}
                  alt={product.name}
                  fill
                  className="object-cover"
                />
              </div>
              <div className="p-4">
                <div className="flex items-center justify-between mb-2">
                  <h2 className="text-lg font-semibold">{product.name}</h2>
                  <div className="flex items-center">
                    {product.is_available ? (
                      <span className="text-green-500 flex items-center text-sm">
                        <FiCheckCircle className="mr-1" />
                        Available
                      </span>
                    ) : (
                      <span className="text-red-500 flex items-center text-sm">
                        <FiXCircle className="mr-1" />
                        Unavailable
                      </span>
                    )}
                  </div>
                </div>
                <p className="text-gray-600 text-sm mb-2 line-clamp-2">
                  {product.description}
                </p>
                <p className="text-orange-600 font-bold mb-4">
                  ${product.price.toFixed(2)}
                </p>
                {product.category && (
                  <div className="mb-4">
                    <span className="inline-block bg-gray-100 text-gray-700 text-xs rounded-full px-3 py-1">
                      {product.category}
                    </span>
                  </div>
                )}
                <div className="flex justify-between">
                  <div className="flex space-x-2">
                    <Link href={`/products/${product.id}`}>
                      <Button size="sm" variant="ghost" leftIcon={<FiEye />}>
                        View
                      </Button>
                    </Link>
                    <Link href={`/products/edit/${product.id}`}>
                      <Button size="sm" variant="outline" leftIcon={<FiEdit />}>
                        Edit
                      </Button>
                    </Link>
                  </div>
                  <Button
                    size="sm"
                    variant="danger"
                    leftIcon={<FiTrash2 />}
                    onClick={() => handleDeleteClick(product)}
                  >
                    Delete
                  </Button>
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {deleteModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg p-6 max-w-md w-full">
            <h3 className="text-xl font-bold mb-4">Confirm Delete</h3>
            <p className="mb-6">
              Are you sure you want to delete "{productToDelete?.name}"? This
              action cannot be undone.
            </p>
            <div className="flex justify-end space-x-4">
              <Button variant="ghost" onClick={() => setDeleteModalOpen(false)}>
                Cancel
              </Button>
              <Button variant="danger" onClick={handleDeleteConfirm}>
                Delete
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
