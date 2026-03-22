import React from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Dashboard from "./pages/Dashboard";
import Person from "./pages/person";
import Landing from "./pages/landing";


const App: React.FC = () => {
  
  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={<Landing onLogin={() => {}} />}
        />
 <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/person" element={<Person onComplete={() => {}} />} />
      </Routes>
    </BrowserRouter>
  );
};

export default App;
