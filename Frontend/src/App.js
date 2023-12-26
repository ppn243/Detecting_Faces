import React from "react";
import { Home, Information } from "./pages";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";

function App() {
  return (
    <div className="App">
      <Router>
        <Routes>
          <Route path="/home" element={<Home />}></Route>
          <Route path="/info" element={<Information />}></Route>
        </Routes>
      </Router>
    </div>
  );
}

export default App;
