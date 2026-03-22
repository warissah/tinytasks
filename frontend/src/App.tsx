import React, { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Landing from "./pages/landing"; // <-- lowercase l
import Dashboard from "./pages/Dashboard";
import Person from "./pages/person";


const App: React.FC = () => {
  const [loggedIn, setLoggedIn] = useState(false);

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={<Landing onLogin={() => setLoggedIn(true)} />}
        />
 <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/person" element={<Person onComplete={() => {}} />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
