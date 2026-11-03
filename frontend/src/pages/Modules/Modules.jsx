import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import styles from "./Modules.module.css";
import api from "../../services/api";
import DashboardNavbar from "../../components/DashboardNavbar/DashboardNavbar";
import Footer from "../../components/Footer/Footer";

export default function Modules() {
  const location = useLocation();
  const navigate = useNavigate();

  const subject = location.state?.subject;
  const role = location.state?.role || localStorage.getItem("role");
  const branch = location.state?.branch;
  const semester = location.state?.semester;
  const isTeacher = role === "teacher";

  const [modules, setModules] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!subject?.id) {
      setError("Subject details are missing. Please select a subject again.");
      setLoading(false);
      return;
    }

    const fetchModules = async () => {
      try {
        setLoading(true);
        setError("");

        const response = await api.get("/modules/", {
          params: { subject_id: subject.id },
        });

        setModules(response.data.modules || []);
      } catch (err) {
        console.error("Could not load modules:", err);
        setError("Could not load modules. Please try again.");
      } finally {
        setLoading(false);
      }
    };

    fetchModules();
  }, [subject?.id]);

  const handleBackToSubjects = () => {
    navigate("/subjects", {
      state: { branch, semester, role },
    });
  };

  const handleOpenMaterials = (module, openUpload = false) => {
    navigate("/materials", {
      state: {
        subject,
        module,
        branch,
        semester,
        role,
        openUpload,
      },
    });
  };

  if (!subject) {
    return (
      <main className={styles.page}>
        <button
          type="button"
          className={styles.backButton}
          onClick={handleBackToSubjects}
        >
          ← Back to Subjects
        </button>

        <p className={styles.message}>
          Subject details are missing. Please return to the subjects page and
          select a subject.
        </p>
      </main>
    );
  }

  return (
    <>
      <DashboardNavbar />

      <main className={styles.page}>
        <header className={styles.pageHeader}>
          <div className={styles.heading}>
            <p className={styles.eyebrow}>Study Materials</p>
            <h1>
              {subject.name}
              {subject.code ? ` (${subject.code})` : ""}
            </h1>
          </div>

          <button
            type="button"
            className={styles.backButton}
            onClick={handleBackToSubjects}
          >
            ← Back to Subjects
          </button>
        </header>

        <section className={styles.moduleSection}>
          <div className={styles.sectionHeader}>
            <div>
              <h2>Available Modules</h2>
              <p>
                {isTeacher
                  ? "View existing materials or upload new materials for a module."
                  : "Select a module to view its study materials."}
              </p>
            </div>
          </div>

          {loading ? (
            <p className={styles.message}>Loading modules...</p>
          ) : error ? (
            <p className={`${styles.message} ${styles.error}`}>{error}</p>
          ) : modules.length === 0 ? (
            <div className={styles.emptyState}>
              <h3>No modules added yet</h3>
              <p>
                {isTeacher
                  ? "Go back to the subjects page to add a module."
                  : "Your teacher has not added any modules for this subject yet."}
              </p>
            </div>
          ) : (
            <div className={styles.moduleGrid}>
              {modules.map((module) => (
                <article className={styles.moduleCard} key={module.id}>
                  <div className={styles.moduleNumber}>
                    Module {module.number}
                  </div>

                  <h3>{module.name}</h3>

                  {module.description ? (
                    <p className={styles.description}>{module.description}</p>
                  ) : (
                    <p className={styles.noDescription}>
                      No description provided.
                    </p>
                  )}

                  <div className={styles.moduleActions}>
                    <button
                      type="button"
                      className={styles.materialsButton}
                      onClick={() => handleOpenMaterials(module)}
                    >
                      View Materials
                    </button>

                    {isTeacher && (
                      <button
                        type="button"
                        className={`${styles.materialsButton} ${styles.uploadButton}`}
                        onClick={() => handleOpenMaterials(module, true)}
                      >
                        📑 Upload Materials
                      </button>
                    )}
                  </div>
                </article>
              ))}
            </div>
          )}
        </section>
      </main>
    </>
  );
}
