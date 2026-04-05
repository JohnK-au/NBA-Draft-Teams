import { Dashboard } from "./pages/Dashboard";
import "./styles.css";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import { AllTime } from "./pages/AllTime";

export default function App() {
  return (
    <BrowserRouter>
      <nav>
        <Link to="/">Season</Link>
        <Link to="/alltime">All-Time</Link>
      </nav>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/alltime" element={<AllTime />} />
      </Routes>
    </BrowserRouter>
  );
}
