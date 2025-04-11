"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { useCart } from "@/contexts/CartContext";
import Button from "@/components/ui/Button";
import { formatCurrency } from "@/lib/utils";
import { FiShoppingCart, FiMenu, FiX, FiUser } from "react-icons/fi";

const Navbar = () => {
  const pathname = usePathname();
  const { user, logout, isAuthenticated, isCustomer, isHawker } = useAuth();
  const { getTotalQuantity, getTotalAmount } = useCart();
  const [isMenuOpen, setIsMenuOpen] = useState(false);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const handleLogout = async () => {
    await logout();
    setIsMenuOpen(false);
  };

  const customerLinks = [
    { href: "/", label: "Home" },
    { href: "/hawkers", label: "Hawkers" },
    { href: "/orders", label: "My Orders" },
  ];

  const hawkerLinks = [
    { href: "/", label: "Home" },
    { href: "/products/manage", label: "My Products" },
    { href: "/orders/manage", label: "Orders" },
    { href: "/hawker/route", label: "Delivery Route" },
  ];

  const navigationLinks = isHawker ? hawkerLinks : customerLinks;

  return (
    <header className="bg-white shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center">
            <span className="text-orange-600 font-bold text-xl">
              HawkeRoute
            </span>
          </Link>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-8">
            {navigationLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className={`text-gray-600 hover:text-orange-600 ${
                  pathname === link.href ? "text-orange-600 font-medium" : ""
                }`}
              >
                {link.label}
              </Link>
            ))}
          </nav>

          {/* Desktop Auth/Cart Actions */}
          <div className="hidden md:flex items-center space-x-4">
            {isAuthenticated ? (
              <>
                {isCustomer && (
                  <Link
                    href="/cart"
                    className="flex items-center text-gray-600 hover:text-orange-600"
                  >
                    <FiShoppingCart className="mr-1" />
                    <span className="mr-1">{getTotalQuantity()}</span>
                    <span>({formatCurrency(getTotalAmount())})</span>
                  </Link>
                )}
                <div className="relative group">
                  <button className="flex items-center text-gray-600 hover:text-orange-600">
                    <FiUser className="mr-1" />
                    <span>{user?.name || "Account"}</span>
                  </button>
                  <div className="absolute right-0 w-48 py-2 mt-2 bg-white rounded-md shadow-xl z-20 hidden group-hover:block">
                    <Link
                      href="/profile"
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-orange-50"
                    >
                      Profile
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-orange-50"
                    >
                      Logout
                    </button>
                  </div>
                </div>
              </>
            ) : (
              <>
                <Link href="/login">
                  <Button variant="ghost" size="sm">
                    Login
                  </Button>
                </Link>
                <Link href="/register">
                  <Button size="sm">Register</Button>
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="md:hidden">
            <button
              onClick={toggleMenu}
              className="text-gray-600 hover:text-orange-600"
            >
              {isMenuOpen ? <FiX size={24} /> : <FiMenu size={24} />}
            </button>
          </div>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-3 border-t">
            <div className="space-y-3">
              {navigationLinks.map((link) => (
                <Link
                  key={link.href}
                  href={link.href}
                  onClick={() => setIsMenuOpen(false)}
                  className={`block py-2 text-gray-600 hover:text-orange-600 ${
                    pathname === link.href ? "text-orange-600 font-medium" : ""
                  }`}
                >
                  {link.label}
                </Link>
              ))}

              {isCustomer && (
                <Link
                  href="/cart"
                  onClick={() => setIsMenuOpen(false)}
                  className="flex items-center py-2 text-gray-600 hover:text-orange-600"
                >
                  <FiShoppingCart className="mr-2" />
                  <span>Cart ({getTotalQuantity()})</span>
                </Link>
              )}

              <Link
                href="/profile"
                onClick={() => setIsMenuOpen(false)}
                className="block py-2 text-gray-600 hover:text-orange-600"
              >
                Profile
              </Link>

              {isAuthenticated ? (
                <button
                  onClick={handleLogout}
                  className="block w-full text-left py-2 text-gray-600 hover:text-orange-600"
                >
                  Logout
                </button>
              ) : (
                <div className="flex flex-col space-y-2 pt-2">
                  <Link href="/login" onClick={() => setIsMenuOpen(false)}>
                    <Button variant="ghost" fullWidth>
                      Login
                    </Button>
                  </Link>
                  <Link href="/register" onClick={() => setIsMenuOpen(false)}>
                    <Button fullWidth>Register</Button>
                  </Link>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </header>
  );
};

export default Navbar;
