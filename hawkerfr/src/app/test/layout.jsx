"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function TestLayout({ children }) {
  const pathname = usePathname();
  
  const navItems = [
    { path: "/test", label: "Overview" },
    { path: "/test/map", label: "Map Testing" },
  ];
  
  return (
    <div className="container mx-auto px-4 py-8">
      {/* Warning banner */}
      <div className="bg-yellow-50 border-l-4 border-yellow-400 p-4 mb-6">
        <div className="flex">
          <div className="flex-shrink-0">
            <svg className="h-5 w-5 text-yellow-400" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
              <path fillRule="evenodd" d="M8.485 3.495c.673-1.167 2.357-1.167 3.03 0l6.28 10.875c.673 1.167-.17 2.625-1.516 2.625H3.72c-1.347 0-2.189-1.458-1.515-2.625L8.485 3.495zM10 6a.75.75 0 01.75.75v3.5a.75.75 0 01-1.5 0v-3.5A.75.75 0 0110 6zm0 9a1 1 0 100-2 1 1 0 000 2z" clipRule="evenodd" />
            </svg>
          </div>
          <div className="ml-3">
            <p className="text-sm text-yellow-800">
              <strong>Test Environment</strong> - This section is for testing purposes only.
            </p>
          </div>
        </div>
      </div>
      
      {/* Navigation tabs */}
      <div className="border-b border-gray-200 mb-6">
        <nav className="-mb-px flex space-x-6">
          {navItems.map((item) => {
            const isActive = pathname === item.path;
            return (
              <Link 
                key={item.path} 
                href={item.path}
                className={`whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm ${
                  isActive
                    ? "border-orange-500 text-orange-600"
                    : "border-transparent text-gray-700 hover:text-gray-900 hover:border-gray-300"
                }`}
              >
                {item.label}
              </Link>
            );
          })}
        </nav>
      </div>
      
      {/* Content */}
      {children}
    </div>
  );
} 