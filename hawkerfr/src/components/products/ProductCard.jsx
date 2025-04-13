import React, { useState } from "react";
import Image from "next/image";
import Link from "next/link";
import { formatCurrency } from "@/lib/utils";
import Button from "@/components/ui/Button";

const ProductCard = ({ product, onAddToCart }) => {
  const { id, name, description, price, image_url, is_available } = product;
  const [imgError, setImgError] = useState(false);

  // Fallback image
  const defaultImg = "/images/placeholder.jpg";
  // Use default image if no image_url or if there was an error loading the image
  const imageSrc = imgError || !image_url ? defaultImg : image_url;

  // Handle adding to cart with simplified product object
  const handleAddToCart = () => {
    if (onAddToCart) {
      const simplifiedProduct = {
        id,
        name,
        price,
      };
      onAddToCart(simplifiedProduct);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden transition-transform hover:shadow-lg hover:-translate-y-1">
      <div className="relative h-48">
        {/* Use a div with background-image for better fallback handling */}
        <div 
          className="w-full h-full bg-cover bg-center"
          style={{ 
            backgroundImage: `url(${imageSrc})`,
            backgroundSize: 'contain',
            backgroundPosition: 'center',
            backgroundRepeat: 'no-repeat',
            backgroundColor: '#f3f4f6' // light gray background
          }}
        >
          {!is_available && (
            <div className="absolute inset-0 bg-black bg-opacity-60 flex items-center justify-center">
              <span className="text-white font-medium text-lg">Out of Stock</span>
            </div>
          )}
        </div>
      </div>

      <div className="p-4">
        <h3 className="text-lg font-semibold text-gray-900 truncate">{name}</h3>
        <p className="mt-1 text-sm text-gray-500 line-clamp-2 h-10">
          {description || "No description available"}
        </p>

        <div className="mt-3 flex items-center justify-between">
          <span className="text-orange-600 font-bold">
            {formatCurrency(price)}
          </span>
          <div className="flex space-x-2">
            
            <Button
              size="sm"
              disabled={!is_available}
              onClick={handleAddToCart}
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
