import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./StudentDashboard.module.css";
import dashboardData from "../../data/studentDashboard.json";
import api from "../../services/api";
import DashboardNavbar from "../../components/DashboardNavbar/DashboardNavbar";
import Footer from "../../components/Footer/Footer";

function StudentDashboard() {
  const navigate = useNavigate();

  const [userRole, setUserRole] = useState(localStorage.getItem("role") || "");

  const [branches, setBranches] = useState([]);
  const [selectedBranch, setSelectedBranch] = useState(null);

  const [schemes, setSchemes] = useState([]);
  const [selectedScheme, setSelectedScheme] = useState(null);

  const [semesters, setSemesters] = useState([]);
  const [selectedSemester, setSelectedSemester] = useState(null);

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  const [showBranches, setShowBranches] = useState(false);

  const [schemeLoading, setSchemeLoading] = useState(false);
  const [schemeError, setSchemeError] = useState("");

  const [semesterLoading, setSemesterLoading] = useState(false);
  const [semesterError, setSemesterError] = useState("");

  // Load user profile and branches.
  useEffect(() => {
    const token = localStorage.getItem("accessToken");

    if (!token) {
      navigate("/student/login");
      return;
    }

    const loadDashboard = async () => {
      try {
        const profileResponse = await api.get("profile/", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        const profile = profileResponse.data;

        const role =
          profile.role ||
          profile.profile?.role ||
          profile.user?.role ||
          localStorage.getItem("role") ||
          "";

        setUserRole(role);

        if (role) {
          localStorage.setItem("role", role);
        }

        const branchResponse = await api.get("branches/", {
          headers: {
            Authorization: `Bearer ${token}`,
          },
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

  // Load schemes when a branch is selected.
  const handleBranchClick = async (branch) => {
    setSelectedBranch(branch);
    setSelectedScheme(null);
    setSelectedSemester(null);

    setSchemes([]);
    setSemesters([]);

    setSchemeError("");
    setSemesterError("");
    setSchemeLoading(true);

    try {
      const response = await api.get(`schemes/?branch_id=${branch.id}`);

      const data = response.data;

      setSchemes(data.schemes ?? data);
    } catch (err) {
      console.error("Scheme API error:", err.response?.data || err);

      setSchemeError("Could not load schemes. Please try again.");
    } finally {
      setSchemeLoading(false);
    }
  };

  // Load semesters when a scheme is selected.
  const handleSchemeClick = async (scheme) => {
    setSelectedScheme(scheme);
    setSelectedSemester(null);
    setSemesters([]);
    setSemesterError("");
    setSemesterLoading(true);

    try {
      const response = await api.get(`semesters/?scheme_id=${scheme.id}`);

      const data = response.data;

      setSemesters(data.semesters ?? data);
    } catch (err) {
      console.error("Semester API error:", err.response?.data || err);

      setSemesterError("Could not load semesters. Please try again.");
    } finally {
      setSemesterLoading(false);
    }
  };

  const isTeacher = userRole === "teacher";

  return (
    <main className={styles.dashboardPage}>
      <DashboardNavbar isTeacher={isTeacher} />

      <section className={styles.dashboardContent}>
        <div className={styles.dashboardIntro}>
          <h1>{isTeacher ? "Teacher Dashboard" : dashboardData.title}</h1>

          <p>
            {isTeacher
              ? "Choose a branch, scheme, and semester to manage subjects and study materials."
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

        {/* Branch selection */}
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
                  style={{
                    animationDelay: `${index * 100}ms`,
                  }}
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

        {/* Scheme selection */}
        {selectedBranch && !selectedScheme && (
          <section className={styles.semesterSection}>
            <button
              type="button"
              className={styles.backButton}
              onClick={() => {
                setSelectedBranch(null);
                setSchemes([]);
                setSchemeError("");
              }}
            >
              ← Back to branches
            </button>

            <h2>{selectedBranch.name} — Choose Scheme</h2>

            {schemeLoading && <p>Loading schemes...</p>}

            {schemeError && <p className={styles.error}>{schemeError}</p>}

            {!schemeLoading && !schemeError && schemes.length === 0 && (
              <p>No schemes are available for this branch.</p>
            )}

            {!schemeLoading && !schemeError && schemes.length > 0 && (
              <div className={styles.semesterGrid}>
                {schemes.map((scheme) => (
                  <button
                    key={scheme.id}
                    type="button"
                    className={styles.semesterCard}
                    onClick={() => handleSchemeClick(scheme)}
                  >
                    {scheme.name}
                  </button>
                ))}
              </div>
            )}
          </section>
        )}

        {/* Semester selection */}
        {selectedBranch && selectedScheme && !selectedSemester && (
          <section className={styles.semesterSection}>
            <button
              type="button"
              className={styles.backButton}
              onClick={() => {
                setSelectedScheme(null);
                setSemesters([]);
                setSemesterError("");
              }}
            >
              ← Back to schemes
            </button>

            <h2>
              {selectedBranch.name} — {selectedScheme.name} — Choose Semester
            </h2>

            {semesterLoading && <p>Loading semesters...</p>}

            {semesterError && <p className={styles.error}>{semesterError}</p>}

            {!semesterLoading && !semesterError && semesters.length === 0 && (
              <p>No semesters are available for this scheme.</p>
            )}

            {!semesterLoading && !semesterError && semesters.length > 0 && (
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
                          scheme: selectedScheme,
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
      </section>
    </main>
  );
}

export default StudentDashboard;
