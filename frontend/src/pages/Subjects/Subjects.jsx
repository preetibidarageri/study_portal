import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import api from "../../services/api";
import styles from "./Subjects.module.css";
import Navbar from "../../components/Navbar/Navbar";
import DashboardNavbar from "../../components/DashboardNavbar/DashboardNavbar";

function Subjects() {
  const { state } = useLocation();
  const navigate = useNavigate();

  const branch = state?.branch;
  const semester = state?.semester;
  const role = state?.role || localStorage.getItem("role") || "";
  const isTeacher = role === "teacher";

  const [subjects, setSubjects] = useState([]);
  const [name, setName] = useState("");
  const [code, setCode] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  const [showModulePopup, setShowModulePopup] = useState(false);
  const [selectedSubject, setSelectedSubject] = useState(null);
  const [moduleForm, setModuleForm] = useState({
    number: "",
    name: "",
    description: "",
  });

  useEffect(() => {
    if (!branch?.id || !semester?.id) {
      navigate("/dashboard", { replace: true });
      return;
    }

    loadSubjects();
  }, [branch?.id, semester?.id, navigate]);

  const loadSubjects = async () => {
    setLoading(true);
    setError("");

    try {
      const response = await api.get("subjects/", {
        params: {
          branch_id: branch.id,
          semester_id: semester.id,
        },
      });

      const data = response.data;
      setSubjects(data.subjects ?? data.results ?? data);
    } catch (err) {
      console.error("Subjects API error:", err.response?.data || err);
      setError(
        err.response?.data?.detail ||
          "Could not load subjects. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  const handleAddSubject = async (event) => {
    event.preventDefault();
    setError("");
    setSuccess("");
    setSaving(true);

    try {
      await api.post("subjects/", {
        branch: branch.id,
        semester: semester.id,
        name: name.trim(),
        code: code.trim(),
      });

      setName("");
      setCode("");
      setSuccess("Subject added successfully.");
      await loadSubjects();
    } catch (err) {
      console.error("Add subject error:", err.response?.data || err);
      const data = err.response?.data;

      setError(
        data?.detail ||
          data?.name?.[0] ||
          data?.code?.[0] ||
          data?.semester?.[0] ||
          "Could not add the subject. Please check the details.",
      );
    } finally {
      setSaving(false);
    }
  };

  const handleAddModule = (subject) => {
    setSelectedSubject(subject);
    setModuleForm({ number: "", name: "", description: "" });
    setShowModulePopup(true);
  };

  const handleModuleChange = (event) => {
    setModuleForm({
      ...moduleForm,
      [event.target.name]: event.target.value,
    });
  };

  const handleModuleSubmit = async (event) => {
    event.preventDefault();

    try {
      await api.post("/modules/", {
        subject: selectedSubject.id,
        number: Number(moduleForm.number),
        name: moduleForm.name,
        description: moduleForm.description,
      });

      setShowModulePopup(false);
      setModuleForm({ number: "", name: "", description: "" });
      alert("Module added successfully.");
    } catch (error) {
      console.error("Error adding module:", error);
      alert(error.response?.data?.detail || "Could not add module.");
    }
  };

  const handleViewModules = (subject) => {
    navigate("/modules", {
      state: {
        subject,
        branch,
        semester,
        role,
      },
    });
  };

  if (!branch || !semester) return null;

  return (
    <>
      <DashboardNavbar />

      <main className={styles.page}>
        <header className={styles.pageTop}>
          <div className={styles.pageTitleGroup}>
            <p className={styles.subtitle}>
              {branch.name} — {semester.name || `Semester ${semester.number}`}{" "}
              Subjects
            </p>
            {/* <h1 className={styles.heading}>Subjects</h1> */}
          </div>

          <button
            type="button"
            className={styles.backButton}
            onClick={() => navigate("/dashboard")}
          >
            ← Back to Branches
          </button>
        </header>

        {isTeacher && (
          <>
            <h2 className={styles.sectionTitle}>Add subjects</h2>

            <section className={styles.section}>
              <form className={styles.form} onSubmit={handleAddSubject}>
                <label className={styles.field}>
                  Subject name
                  <input
                    className={styles.input}
                    value={name}
                    onChange={(event) => setName(event.target.value)}
                    required
                  />
                </label>

                <label className={styles.field}>
                  Subject code
                  <input
                    className={styles.input}
                    value={code}
                    onChange={(event) => setCode(event.target.value)}
                    required
                  />
                </label>

                <button
                  className={styles.submitButton}
                  type="submit"
                  disabled={saving}
                >
                  {saving ? "Adding..." : "Add subject"}
                </button>
              </form>
            </section>
          </>
        )}

        {error && (
          <p className={`${styles.message} ${styles.error}`}>{error}</p>
        )}

        {success && (
          <p className={`${styles.message} ${styles.success}`}>{success}</p>
        )}

        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Available subjects</h2>

          {loading ? (
            <p className={styles.message}>Loading subjects...</p>
          ) : subjects.length === 0 ? (
            <p className={styles.message}>
              No subjects have been added for this semester yet.
            </p>
          ) : (
            <ul className={styles.subjectList}>
              {subjects.map((subject) => (
                <li className={styles.subjectCard} key={subject.id}>
                  <p className={styles.subjectName}>{subject.name}</p>
                  <span className={styles.subjectCode}>{subject.code}</span>

                  {role === "teacher" && (
                    <button
                      type="button"
                      className={styles.addModuleButton}
                      onClick={() => handleAddModule(subject)}
                    >
                      + Add Module
                    </button>
                  )}

                  <button
                    type="button"
                    className={styles.viewModulesButton}
                    onClick={() => handleViewModules(subject)}
                  >
                    View Modules
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
      </main>
      {showModulePopup && selectedSubject && (
        <div className={styles.modalOverlay}>
          <div className={styles.modal}>
            <h2>Add Module</h2>
            <p>{selectedSubject.name}</p>

            <form onSubmit={handleModuleSubmit}>
              <label>
                Module Number
                <input
                  type="number"
                  name="number"
                  min="1"
                  value={moduleForm.number}
                  onChange={handleModuleChange}
                  required
                />
              </label>

              <label>
                Module Name
                <input
                  type="text"
                  name="name"
                  value={moduleForm.name}
                  onChange={handleModuleChange}
                  required
                />
              </label>

              <label>
                Description / Syllabus
                <textarea
                  name="description"
                  value={moduleForm.description}
                  onChange={handleModuleChange}
                />
              </label>

              <div className={styles.modalActions}>
                <button type="submit">Add Module</button>
                <button type="button" onClick={() => setShowModulePopup(false)}>
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}

export default Subjects;
