import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import styles from "./StudentLogin.module.css";
import loginData from "../../data/studentLogin.json";
import api from "../../services/api";

export default function StudentLogin() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    setFormData({ ...formData, [event.target.name]: event.target.value });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);
    try {
      const response = await api.post("token/", formData);
      localStorage.setItem("accessToken", response.data.access);
      localStorage.setItem("refreshToken", response.data.refresh);
      const profileResponse = await api.get("profile/", {
        headers: {
          Authorization: `Bearer ${response.data.access}`,
        },
      });

      if (profileResponse.data.role !== "student") {
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
        setError("This login is only for students.");
        return;
      }
      navigate("/dashboard");
    } catch (err) {
      localStorage.removeItem("accessToken");
      localStorage.removeItem("refreshToken");

      setError(
        err.response?.data?.detail ||
          "Login failed. Please check your username and password.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.loginPage}>
      <div className={styles.loginCard}>
        <h1>{loginData.title}</h1>
        <p>{loginData.subtitle}</p>
        <form onSubmit={handleSubmit}>
          <label htmlFor="username">{loginData.fields.username.label}</label>
          <input
            id="username"
            type="text"
            name="username"
            placeholder={loginData.fields.username.placeholder}
            value={formData.username}
            onChange={handleChange}
            required
          />

          <label htmlFor="password">{loginData.fields.password.label}</label>
          <input
            id="password"
            type="password"
            name="password"
            placeholder={loginData.fields.password.placeholder}
            value={formData.password}
            onChange={handleChange}
            required
          />

          {error && <p className={styles.error}>{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? "Logging in..." : loginData.button}
          </button>
        </form>

        <div className={styles.registerText}>
          {loginData.registerText}{" "}
          <Link to="/register">{loginData.registerLinkText}</Link>
        </div>
      </div>
    </div>
  );
}
