import React, { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Landing from "./pages/landing"; // <-- lowercase l
import Dashboard from "./pages/Dashboard";
import Person from "./person";


const App: React.FC = () => {
  const [loggedIn, setLoggedIn] = useState(false);

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={<Landing onLogin={() => setLoggedIn(true)} />}
        />
        <Route
          path="/dashboard"
          element={loggedIn ? <Dashboard /> : <Navigate to="/" replace />}
        />
        <Route
          path="/person"
          element={<Person onComplete={(data) => console.log("User Preferences:", data)} />}
        />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
