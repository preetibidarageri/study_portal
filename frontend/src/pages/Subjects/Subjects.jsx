import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import api from "../../services/api";
import styles from "./Subjects.module.css";

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

  useEffect(() => {
    if (!branch?.id || !semester?.id) {
      navigate("/dashboard", { replace: true });
      return;
    }

    loadSubjects();
    // eslint-disable-next-line react-hooks/exhaustive-deps
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

  if (!branch || !semester) return null;

  return (
    <main className={styles.page}>
      <button
        type="button"
        className={styles.backButton}
        onClick={() => navigate("/dashboard")}
      >
        ← Back to dashboard
      </button>

      <h1 className={styles.heading}>Subjects</h1>
      <p className={styles.subtitle}>
        {branch.name} — {semester.name || `Semester ${semester.number}`}
      </p>

      {isTeacher && (
        <section className={styles.section}>
          <h2 className={styles.sectionTitle}>Add subject</h2>

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
      )}

      {error && <p className={`${styles.message} ${styles.error}`}>{error}</p>}
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
              </li>
            ))}
          </ul>
        )}
      </section>
    </main>
  );
}

export default Subjects;
