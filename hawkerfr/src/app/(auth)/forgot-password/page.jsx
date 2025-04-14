"use client";

export default function ForgotPassword() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full p-6 bg-white rounded-lg shadow-md">
        <h2 className="text-2xl font-bold text-center text-gray-800 mb-4">
          Password Reset
        </h2>
        <p className="text-center text-gray-600 mb-4">
          This feature is not yet implemented. Please check back later.
        </p>
        <div className="text-center">
          <a
            href="/login"
            className="text-blue-600 hover:text-blue-800 font-medium"
          >
            Return to login
          </a>
        </div>
      </div>
    </div>
  );
}

