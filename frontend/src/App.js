import { useState, useEffect } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate, useLocation } from "react-router-dom";
import axios from "axios";
import Login from "./components/Login";
import Register from "./components/Register";
import Dashboard from "./components/Dashboard";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api/v1`;

axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

const logEvent = (eventType, details = {}) => {
  const LOG_KEY = "frontend_logs";
  const logs = JSON.parse(localStorage.getItem(LOG_KEY)) || [];
  const newLog = {
    timestamp: new Date().toISOString(),
    event: eventType,
    details,
  };
  logs.push(newLog);
  localStorage.setItem(LOG_KEY, JSON.stringify(logs));
  console.log("[LOGGED EVENT]:", newLog);
};

function RouteLogger() {
  const location = useLocation();
  useEffect(() => {
    logEvent("Page Navigation", { path: location.pathname });
  }, [location]);
  return null;
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const handleClick = (e) => {
      logEvent("Click", {
        tag: e.target.tagName,
        text: e.target.innerText?.slice(0, 50),
      });
    };
    window.addEventListener("click", handleClick);
    return () => window.removeEventListener("click", handleClick);
  }, []);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    const token = localStorage.getItem("token");
    if (token) {
      try {
        const response = await axios.get(`${API}/auth/me`);
        setUser(response.data);
        setIsAuthenticated(true);
        logEvent("User Authenticated", { email: response.data.email });
      } catch (error) {
        localStorage.removeItem("token");
        setIsAuthenticated(false);
        logEvent("Auth Failed", { error: error.message });
      }
    }
    setLoading(false);
  };

  const handleLogout = () => {
    localStorage.removeItem("token");
    setIsAuthenticated(false);
    setUser(null);
    logEvent("User Logged Out");
  };

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <div className="App">
      <BrowserRouter>
        <RouteLogger />
        <Routes>
          <Route
            path="/login"
            element={
              !isAuthenticated ? (
                <Login setIsAuthenticated={setIsAuthenticated} setUser={setUser} API={API} />
              ) : (
                <Navigate to="/dashboard" />
              )
            }
          />
          <Route
            path="/register"
            element={
              !isAuthenticated ? (
                <Register setIsAuthenticated={setIsAuthenticated} setUser={setUser} API={API} />
              ) : (
                <Navigate to="/dashboard" />
              )
            }
          />
          <Route
            path="/dashboard"
            element={
              isAuthenticated ? (
                <Dashboard user={user} handleLogout={handleLogout} API={API} />
              ) : (
                <Navigate to="/login" />
              )
            }
          />
          <Route path="/" element={<Navigate to={isAuthenticated ? "/dashboard" : "/login"} />} />
        </Routes>
      </BrowserRouter>
    </div>
  );
}

export default App;
