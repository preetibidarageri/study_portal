import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import styles from "./Register.module.css";
import registerData from "../../data/register.json";
import api from "../../services/api";

function Register() {
  const navigate = useNavigate();

  const [formData, setFormData] = useState({
    username: "",
    first_name: "",
    last_name: "",
    email: "",
    password: "",
    role: "student",
  });

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (event) => {
    setFormData({
      ...formData,
      [event.target.name]: event.target.value,
    });
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setError("");
    setLoading(true);

    try {
      await api.post("register/", formData);

      if (formData.role === "student") {
        navigate("/student/login");
      } else {
        navigate("/teacher/login");
      }
    } catch (err) {
      console.error(
        "Registration error:",
        err.response?.status,
        err.response?.data,
        err.message,
      );

      const responseData = err.response?.data;
      setError(
        responseData
          ? JSON.stringify(responseData)
          : err.message || "Could not reach the registration API.",
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.registerPage}>
      <div className={styles.registerCard}>
        <h1>{registerData.title}</h1>
        <p>{registerData.subtitle}</p>

        <form onSubmit={handleSubmit}>
          {["username", "first_name", "last_name", "email", "password"].map(
            (field) => (
              <div className={styles.formGroup} key={field}>
                <label htmlFor={field}>
                  {registerData.fields[field].label}
                </label>
                <input
                  id={field}
                  name={field}
                  type={
                    field === "password"
                      ? "password"
                      : field === "email"
                        ? "email"
                        : "text"
                  }
                  placeholder={registerData.fields[field].placeholder}
                  value={formData[field]}
                  onChange={handleChange}
                  required
                />
              </div>
            ),
          )}

          <div className={styles.formGroup}>
            <label htmlFor="role">{registerData.fields.role.label}</label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
              required
            >
              <option value="student">
                {registerData.fields.role.student}
              </option>
              <option value="teacher">
                {registerData.fields.role.teacher}
              </option>
            </select>
          </div>

          {error && <p className={styles.error}>{error}</p>}

          <button type="submit" disabled={loading}>
            {loading ? "Creating account..." : registerData.button}
          </button>
        </form>

        <div className={styles.loginLinks}>
          <p>{registerData.loginText}</p>
          <Link to="/student/login">{registerData.studentLoginLink}</Link>
          {" | "}
          <Link to="/teacher/login">{registerData.teacherLoginLink}</Link>
        </div>
      </div>
    </div>
  );
}

export default Register;
