import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./StudentDashboard.module.css";
import dashboardData from "../../data/studentDashboard.json";
import api from "../../services/api";

function StudentDashboard() {
  const navigate = useNavigate();

  const [userRole, setUserRole] = useState(localStorage.getItem("role") || "");
  const [branches, setBranches] = useState([]);
  const [selectedBranch, setSelectedBranch] = useState(null);
  const [semesters, setSemesters] = useState([]);
  const [selectedSemester, setSelectedSemester] = useState(null);

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [showBranches, setShowBranches] = useState(false);
  const [semesterLoading, setSemesterLoading] = useState(false);
  const [semesterError, setSemesterError] = useState("");

  useEffect(() => {
    const token = localStorage.getItem("accessToken");

    if (!token) {
      navigate("/student/login");
      return;
    }

    const loadDashboard = async () => {
      try {
        // Read the logged-in user's role.
        const profileResponse = await api.get("profile/", {
          headers: { Authorization: `Bearer ${token}` },
        });

        const profile = profileResponse.data;
        const role =
          profile.role ||
          profile.profile?.role ||
          profile.user?.role ||
          localStorage.getItem("role") ||
          "";

        setUserRole(role);
        if (role) localStorage.setItem("role", role);

        // Load branches for both students and teachers.
        const branchResponse = await api.get("branches/", {
          headers: { Authorization: `Bearer ${token}` },
        });

        const branchList = branchResponse.data.branches;

        if (Array.isArray(branchList)) {
          setBranches(branchList);
        } else {
          setError("The branches API did not return a branch list.");
        }
      } catch (err) {
        console.error(
          "Dashboard API error:",
          err.response?.status,
          err.response?.data,
        );
        setError(
          err.response?.data?.detail ||
            "Could not load the dashboard. Please log in again.",
        );
      } finally {
        setLoading(false);
      }
    };
    loadDashboard();
  }, [navigate]);

  const handleLogout = () => {
    localStorage.removeItem("accessToken");
    localStorage.removeItem("refreshToken");
    localStorage.removeItem("role");
    navigate(userRole === "teacher" ? "/teacher/login" : "/student/login");
  };

  const handleBranchClick = async (branch) => {
    setSelectedBranch(branch);
    setSelectedSemester(null);
    setSemesters([]);
    setSemesterError("");
    setSemesterLoading(true);

    try {
      const response = await api.get(`semesters/?branch_id=${branch.id}`);
      const data = response.data;
      setSemesters(data.semesters ?? data);
    } catch (err) {
      console.error("Semester API error:", err.response?.data || err);
      setSemesterError("Could not load semesters. Please try again.");
    } finally {
      setSemesterLoading(false);
    }
  };

  const handleHome = () => {
    setSelectedBranch(null);
    setSelectedSemester(null);
    setSemesters([]);
    setSemesterError("");
    setShowBranches(false);
  };

  const isTeacher = userRole === "teacher";

  return (
    <main className={styles.dashboardPage}>
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

      <section className={styles.dashboardContent}>
        <div className={styles.dashboardIntro}>
          <h1>{isTeacher ? "Teacher Dashboard" : dashboardData.title}</h1>

          <p>
            {isTeacher
              ? "Choose a branch and semester to manage subjects and study materials."
              : dashboardData.subtitle}
          </p>

          {!selectedBranch && (
            <button
              type="button"
              className={styles.chooseBranchButton}
              onClick={() => setShowBranches(true)}
            >
              Choose Branch
            </button>
          )}
        </div>

        {loading && <p>Loading dashboard...</p>}
        {error && <p className={styles.error}>{error}</p>}

        {!loading &&
          showBranches &&
          !selectedBranch &&
          (branches.length > 0 ? (
            <div className={styles.branchGrid}>
              {branches.map((branch, index) => (
                <button
                  type="button"
                  className={styles.branchCard}
                  key={branch.id}
                  style={{ animationDelay: `${index * 100}ms` }}
                  onClick={() => handleBranchClick(branch)}
                >
                  <span className={styles.branchName}>{branch.name}</span>
                  <span className={styles.cardArrow}>Select branch →</span>
                </button>
              ))}
            </div>
          ) : (
            <p>No branches were returned by the API.</p>
          ))}

        {selectedBranch && !selectedSemester && (
          <section className={styles.semesterSection}>
            <button
              type="button"
              className={styles.backButton}
              onClick={() => {
                setSelectedBranch(null);
                setSemesters([]);
                setSemesterError("");
              }}
            >
              ← Back to branches
            </button>

            <h2>{selectedBranch.name} — Choose Semester</h2>

            {semesterLoading && <p>Loading semesters...</p>}
            {semesterError && <p className={styles.error}>{semesterError}</p>}

            {!semesterLoading && !semesterError && (
              <div className={styles.semesterGrid}>
                {semesters.map((semester) => (
                  <button
                    key={semester.id}
                    type="button"
                    className={styles.semesterCard}
                    onClick={() =>
                      navigate("/subjects", {
                        state: {
                          branch: selectedBranch,
                          semester,
                          role: userRole,
                        },
                      })
                    }
                  >
                    {semester.name || `Semester ${semester.number}`}
                  </button>
                ))}
              </div>
            )}
          </section>
        )}

        {/* {selectedBranch && selectedSemester && (
          <section className={styles.semesterSection}>
            <button
              type="button"
              className={styles.backButton}
              onClick={() => setSelectedSemester(null)}
            >
              ← Back to semesters
            </button>

            <h2>
              {selectedBranch.name} —{" "}
              {selectedSemester.name || `Semester ${selectedSemester.number}`}
            </h2>

            {isTeacher ? (
              <div>
                <p>Manage subjects and study materials for this semester.</p>
                <button
                  type="button"
                  className={styles.chooseBranchButton}
                  onClick={() =>
                    alert(
                      "The Add Subject form will be connected after the subjects API is ready.",
                    )
                  }
                >
                  Add Subject
                </button>
              </div>
            ) : (
              <p>Subjects for this branch and semester will appear here.</p>
            )}
          </section>
        )} */}
      </section>
    </main>
  );
}

export default StudentDashboard;
