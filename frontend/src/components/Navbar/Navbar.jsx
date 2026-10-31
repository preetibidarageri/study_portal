import { useState } from "react";
import styles from "./Navbar.module.css";
import homeData from "../../data/home.json";
import { Link } from "react-router-dom";

export default function Navbar() {
  const [isOpen, setIsOpen] = useState(false);
  const { navbar } = homeData;
  const [isLoginOpen, setIsLoginOpen] = useState(false);

  const toggleMenu = () => {
    setIsOpen(!isOpen);
  };

  return (
    <nav className={styles.navbar}>
      <h2 className={styles.logo}>{navbar.logo}</h2>

      {/* Hamburger Icon */}
      <button
        className={`${styles.hamburger} ${isOpen ? styles.hamburgerActive : ""}`}
        onClick={toggleMenu}
        aria-label="Toggle navigation"
      >
        <span className={styles.bar}></span>
        <span className={styles.bar}></span>
        <span className={styles.bar}></span>
      </button>

      {/* Navigation Container */}
      <div
        className={`${styles.navContainer} ${isOpen ? styles.navContainerActive : ""}`}
      >
        <div className={styles.navLinks}>
          {navbar.links.map((link, index) => (
            <a key={index} href={link.url} onClick={() => setIsOpen(false)}>
              {link.label}
            </a>
          ))}
        </div>

        <div className={styles.navButtons}>
          {navbar.buttons.map((button, index) =>
            button.label === "Login" ? (
              <div className={styles.loginDropdown} key={button.label}>
                <button
                  type="button"
                  className={styles.loginButton}
                  onClick={() => setIsLoginOpen((open) => !open)}
                  aria-expanded={isLoginOpen}
                >
                  Login ▾
                </button>

                {isLoginOpen && (
                  <div className={styles.dropdownMenu}>
                    <Link
                      to="/student/login"
                      onClick={() => setIsLoginOpen(false)}
                    >
                      Student Login
                    </Link>
                    <Link
                      to="/teacher/login"
                      onClick={() => setIsLoginOpen(false)}
                    >
                      Teacher Login
                    </Link>
                  </div>
                )}
              </div>
            ) : (
              <Link
                key={button.label}
                to={button.url}
                className={styles.registerButton}
                onClick={() => setIsOpen(false)}
              >
                {button.label}
              </Link>
            ),
          )}
        </div>
      </div>
    </nav>
  );
}
