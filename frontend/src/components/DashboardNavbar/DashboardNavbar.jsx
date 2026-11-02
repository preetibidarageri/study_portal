import { useNavigate } from "react-router-dom";
import styles from "./DashboardNavbar.module.css";

function DashboardNavbar({ onHome }) {
  const navigate = useNavigate();
  const role = localStorage.getItem("role") || "";
  const isTeacher = role === "teacher";

  const handleHome = () => {
    if (onHome) {
      onHome();
    } else {
      navigate("/dashboard");
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("role");

    navigate(isTeacher ? "/" : "/", {
      replace: true,
    });
  };

  return (
    <header className={styles.navbar}>
      <span className={styles.brand}>
        {isTeacher ? "SKSV Teacher Portal" : "SKSV Study Portal"}
      </span>

      <nav className={styles.navLinks}>
        <button type="button" onClick={handleHome}>
          Home
        </button>

        <button type="button" onClick={handleLogout}>
          Log out
        </button>
      </nav>
    </header>
  );
}

export default DashboardNavbar;
