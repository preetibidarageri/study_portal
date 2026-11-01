import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import styles from "./TeacherLogin.module.css";
import loginData from "../../data/teacherLogin.json";
import api from "../../services/api";
import Navbar from "../../components/Navbar/Navbar";

function TeacherLogin() {
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
      const profileResponse = await api.get("profile/", {
        headers: { Authorization: `Bearer ${response.data.access}` },
      });
      if (profileResponse.data.role !== "teacher") {
        setError("This login is only for teachers.");
        return;
      }
      localStorage.setItem("accessToken", response.data.access);
      localStorage.setItem("refreshToken", response.data.refresh);
      navigate("/dashboard");
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Login failed. Please check your username and password.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Navbar />
      <div className={styles.loginPage}>
        <div className={styles.loginCard}>
          <h1>{loginData.title}</h1>
          <p>{loginData.subtitle}</p>

          <form onSubmit={handleSubmit}>
            <label htmlFor="username">{loginData.fields.username.label}</label>
            <input
              id="username"
              name="username"
              type="text"
              placeholder={loginData.fields.username.placeholder}
              value={formData.username}
              onChange={handleChange}
              required
            />

            <label htmlFor="password">{loginData.fields.password.label}</label>
            <input
              id="password"
              name="password"
              type="password"
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
    </>
  );
}

export default TeacherLogin;
