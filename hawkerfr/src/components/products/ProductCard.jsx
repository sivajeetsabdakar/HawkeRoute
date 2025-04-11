import React from "react";
import Image from "next/image";
import Link from "next/link";
import { formatCurrency } from "@/lib/utils";
import Button from "@/components/ui/Button";

const ProductCard = ({ product, onAddToCart }) => {
  const { id, name, description, price, image_url, is_available } = product;

  // Fallback image if product image is not available
  const imageSrc = image_url || "/images/placeholder-food.jpg";

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden transition-transform hover:shadow-lg hover:-translate-y-1">
      <div className="relative h-48">
        <Image
          src={imageSrc}
          alt={name}
          fill
          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
          className="object-cover"
        />
        {!is_available && (
          <div className="absolute inset-0 bg-black bg-opacity-60 flex items-center justify-center">
            <span className="text-white font-medium text-lg">Out of Stock</span>
          </div>
        )}
      </div>

      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 truncate">{name}</h3>
        <p className="mt-1 text-sm text-gray-500 line-clamp-2 h-10">
          {description}
        </p>

        <div className="mt-3 flex items-center justify-between">
          <span className="text-orange-600 font-bold">
            {formatCurrency(price)}
          </span>
          <div className="flex space-x-2">
            <Link
              href={`/products/${id}`}
              className="text-sm text-gray-600 hover:text-orange-600"
            >
              Details
            </Link>
            <Button
              size="sm"
              disabled={!is_available}
              onClick={() => onAddToCart && onAddToCart(product)}
            >
              Add to Cart
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ProductCard;
