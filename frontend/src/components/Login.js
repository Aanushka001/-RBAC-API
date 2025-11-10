import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import axios from "axios";

const Login = ({ setIsAuthenticated, setUser, API }) => {
  const [formData, setFormData] = useState({
    email: "",
    password: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const response = await axios.post(`${API}/auth/login`, formData);
      localStorage.setItem("token", response.data.access_token);
      setUser(response.data.user);
      setIsAuthenticated(true);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.detail || "Login failed. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container" data-testid="login-page">
      <div className="auth-card">
        <div className="auth-header">
          <h1>Welcome Back</h1>
          <p>Log in to access your dashboard</p>
        </div>

        {error && <div className="error-message" data-testid="error-message">{error}</div>}

        <form onSubmit={handleSubmit} className="auth-form" data-testid="login-form">
          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              required
              data-testid="login-email-input"
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              required
              data-testid="login-password-input"
            />
          </div>

          <button 
            type="submit" 
            className="btn-primary" 
            disabled={loading}
            data-testid="login-submit-button"
          >
            {loading ? "Logging in..." : "Log In"}
          </button>
        </form>

        <div className="auth-footer">
          Don't have an account? <Link to="/register" data-testid="register-link">Register</Link>
        </div>

      </div>
    </div>
  );
};

export default Login;