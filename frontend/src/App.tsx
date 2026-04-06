import { Dashboard } from "./pages/Dashboard";
import "./styles.css";
import { BrowserRouter, Routes, Route, NavLink } from "react-router-dom";
import { AllTime } from "./pages/AllTime";

export default function App() {
  return (
    <BrowserRouter>
      <nav className="navbar">
        <NavLink to="/" className="navbar__link">Current Season</NavLink>
        <NavLink to="/alltime" className="navbar__link">All-Time</NavLink>
      </nav>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/alltime" element={<AllTime />} />
      </Routes>
    </BrowserRouter>
  );
}
