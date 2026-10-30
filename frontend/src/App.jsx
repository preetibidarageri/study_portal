import "./App.css";

function App() {
  return (
    <>
      <div className="app">
        <nav className="navbar">
          <h2 className="logo">SKSV Study Portal</h2>

          <div className="nav-links">
            <a href="/">Home</a>
            <a href="#about">About</a>
            <a href="#contact">Contact</a>
          </div>

          <div className="nav-buttons">
            <button className="login-btn">Login</button>
            <button className="register-btn">Register</button>
          </div>
        </nav>

        <section className="hero">
          <div className="hero-content">
            <h1>Welcome to SKSV Study Material Portal</h1>

            <p>
              Your one-stop destination for engineering study materials. Access
              notes, PDFs and learning resources anytime, anywhere.
            </p>

            <button className="get-started">Get Started</button>
          </div>
        </section>

        <section className="features" id="about">
          <h2>What We Offer</h2>

          <div className="feature-container">
            <div className="feature-card">
              <h3>Study Materials</h3>
              <p>Access subject-wise notes and PDFs.</p>
            </div>

            <div className="feature-card">
              <h3>Semester Wise Learning</h3>
              <p>Find learning materials according to your semester.</p>
            </div>

            <div className="feature-card">
              <h3>Easy Access</h3>
              <p>Access your study resources whenever you need them.</p>
            </div>
          </div>
        </section>

        <footer id="contact">
          <p>© 2026 SKSV Study Material Portal. All rights reserved.</p>
        </footer>
      </div>
    </>
  );
}

export default App;
