# HawkeRoute Prototype

## Problem Statement

In many neighborhoods, cities, and villages across India, local hawkers and street vendors travel long distances daily to sell their goods, often with little knowledge of where demand is highest. This leads to wasted time, increased travel costs, and small profits. Residents also struggle to find and connect with these vendors efficiently, missing out on fresh, local products and services.

## Solution Overview

HawkeRoute is a web-based prototype that connects local hawkers and vendors with residents in their area. The platform helps hawkers optimize their routes using AI, reach more customers, and increase their earnings, while residents can easily discover and interact with nearby vendors.

## Key Features

- **Hawker/Vendor Discovery:** Residents can view a list of active hawkers/vendors, their products, and locations in real-time.
- **AI Chat Assistant:** Integrated Gemini AI chat assistant answers user queries about vendors, products, and platform usage.
- **AI Route Optimization:** Hawkers receive AI-powered route suggestions (using Gemini API) to maximize efficiency and profits.
- **Order Placement & Tracking:** Residents can place orders and track vendor deliveries (prototype feature).

## Google Technologies Used

- **Google IDX Studio:** For cloud-based development and deployment of the web application.
- **Firebase Studio:** For authentication, real-time database, and hosting (if used).
- **Gemini API (Google AI):** For AI-powered chat assistant and route optimization features.
- **Google Maps API:** For geolocation, vendor discovery, and route visualization.

## Tech Stack

- **Frontend:** Next.js (React), Tailwind CSS
- **Backend:** Python (Flask, SQLAlchemy, Celery)
- **Database:** SQL Server (for prototype; can be adapted to Firebase/Firestore)
- **AI:** Gemini API (Google Generative AI)
- **Other:** Google Maps API, Firebase (optional)

## Setup Instructions

### Prerequisites
- Python 3.8+
- Node.js 18+
- Access to Google Gemini API (API key)
- Firebase project for authentication/hosting
- SQL Server running locally or in the cloud

### Backend Setup
1. Clone the repository and navigate to the backend folder:
   ```sh
   git clone <your-repo-link>
   cd backend
   ```
2. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
3. Set up your environment variables in a `.env` file:
   ```env
   DATABASE_URL=mssql+pyodbc://sa:your_password@localhost\\SQLEXPRESS/your_db?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
   GEMINI_API_KEY=your-gemini-api-key
   # Add other keys as needed
   ```
4. Run the backend:
   ```sh
   python run.py
   ```

### Frontend Setup
1. Navigate to the frontend folder:
   ```sh
   cd hawkerfr
   ```
2. Install dependencies:
   ```sh
   npm install
   ```
3. Update the API base URL in `src/lib/api.js` if needed.
4. Run the frontend:
   ```sh
   npm run dev
   ```

### Using the Prototype
- Visit the homepage to discover hawkers/vendors.
- Use the chat button to interact with the Gemini AI assistant.
- (If logged in as a hawker) Access route optimization features.

## License
This project is a prototype for demonstration purposes and is not intended for production use. 