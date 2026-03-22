import React from "react";
import { useNavigate } from "react-router-dom";

interface LandingProps {
  onLogin: () => void;
}

const Landing: React.FC<LandingProps> = ({ onLogin }) => {
  const navigate = useNavigate();

  const handleLogin = () => {
    onLogin();          // update loggedIn state
    navigate("/dashboard"); // navigate to dashboard page
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100">
      <h1 className="text-4xl font-bold mb-6">Landing Page</h1>
      <button
        onClick={handleLogin}
        className="px-6 py-3 bg-blue-500 text-white rounded hover:bg-blue-600"
      >
        Log In
      </button>
    </div>
  );
};

export default Landing;
