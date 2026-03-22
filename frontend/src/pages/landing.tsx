import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./landing.css";

interface LandingProps {
  onLogin: () => void;
}

const Landing: React.FC<LandingProps> = ({ onLogin }) => {
  const navigate = useNavigate();
  const [isSignUp, setIsSignUp] = useState(false);
  const [username, setUsername] = useState("");

  const handleSubmit = () => {
    if (!username.trim()) return;

    onLogin(); // update loggedIn state

    if (isSignUp) {
      navigate("/person"); // first-time user goes to onboarding
    } else {
      navigate("/dashboard"); // returning user goes to dashboard
    }
  };

  return (
    <div className="landing-container">
      <div className="landing-card">
        <h1 className="landing-title">{isSignUp ? "Sign Up" : "Log In"}</h1>
        <input
          type="text"
          placeholder="Enter your username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
          className="landing-input"
        />
        <button onClick={handleSubmit} className="landing-button">
          {isSignUp ? "Get Started" : "Log In"}
        </button>
        <p className="toggle-text">
          {isSignUp ? "Already have an account?" : "New here?"}{" "}
          <span onClick={() => setIsSignUp(!isSignUp)}>
            {isSignUp ? "Log In" : "Sign Up"}
          </span>
        </p>
      </div>
    </div>
  );
};

export default Landing;
