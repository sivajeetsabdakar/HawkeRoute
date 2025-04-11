import React, { forwardRef } from "react";

const Input = forwardRef(
  (
    {
      label,
      id,
      name,
      type = "text",
      placeholder,
      error,
      className = "",
      containerClassName = "",
      labelClassName = "",
      required = false,
      disabled = false,
      ...props
    },
    ref
  ) => {
    const baseInputClasses =
      "w-full rounded-md border py-2 px-3 text-gray-900 shadow-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-orange-500 sm:text-sm";
    const errorInputClasses = error
      ? "border-red-500 focus:ring-red-500"
      : "border-gray-300";
    const disabledClasses = disabled ? "bg-gray-100 cursor-not-allowed" : "";

    return (
      <div className={`${containerClassName}`}>
        {label && (
          <label
            htmlFor={id || name}
            className={`block text-sm font-medium text-gray-700 mb-1 ${labelClassName}`}
          >
            {label}
            {required && <span className="text-red-500 ml-1">*</span>}
          </label>
        )}

        <input
          ref={ref}
          type={type}
          id={id || name}
          name={name}
          placeholder={placeholder}
          className={`${baseInputClasses} ${errorInputClasses} ${disabledClasses} ${className}`}
          disabled={disabled}
          required={required}
          aria-invalid={error ? "true" : "false"}
          aria-describedby={error ? `${name}-error` : undefined}
          {...props}
        />

        {error && (
          <p id={`${name}-error`} className="mt-1 text-sm text-red-600">
            {error}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = "Input";

export default Input;
