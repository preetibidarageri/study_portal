import { useEffect, useState } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import api from "../../services/api";
import DashboardNavbar from "../../components/DashboardNavbar/DashboardNavbar";
import styles from "./Materials.module.css";
import Footer from "../../components/Footer/Footer";

const CATEGORIES = [
  { value: "pdf", label: "PDF Notes" },
  { value: "ppt", label: "PPT Slides" },
  { value: "video", label: "Video Links" },
];

function Materials() {
  const location = useLocation();
  const navigate = useNavigate();

  const { subject, module, branch, semester } = location.state || {};
  const role = location.state?.role || localStorage.getItem("role");
  const isTeacher = role === "teacher";

  const [materials, setMaterials] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [activeCategory, setActiveCategory] = useState("pdf");

  const [showUploadForm, setShowUploadForm] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState("pdf");
  const [heading, setHeading] = useState("");
  const [description, setDescription] = useState("");
  const [file, setFile] = useState(null);
  const [videoUrl, setVideoUrl] = useState("");
  const [formError, setFormError] = useState("");
  const [uploading, setUploading] = useState(false);

  const fetchMaterials = async () => {
    if (!module?.id) {
      setError(
        "Module information is missing. Please go back and select a module.",
      );
      setLoading(false);
      return;
    }

    try {
      setError("");
      const response = await api.get("/materials/", {
        params: { module_id: module.id },
      });

      const data = response.data;
      const materialList = Array.isArray(data)
        ? data
        : data.results || data.materials || [];

      setMaterials(materialList);
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          "Could not load materials. Please try again.",
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchMaterials();
  }, [module?.id]);

  const resetForm = () => {
    setHeading("");
    setDescription("");
    setFile(null);
    setVideoUrl("");
    setSelectedCategory("pdf");
    setFormError("");
  };

  const closeUploadForm = () => {
    setShowUploadForm(false);
    resetForm();
  };

  const handleUpload = async (event) => {
    event.preventDefault();
    setFormError("");

    if (!module?.id) {
      setFormError("Module information is missing.");
      return;
    }

    if (selectedCategory === "video" && !videoUrl.trim()) {
      setFormError("Please enter a video URL.");
      return;
    }

    if (selectedCategory !== "video" && !file) {
      setFormError("Please select a file to upload.");
      return;
    }

    const formData = new FormData();
    formData.append("module", module.id);
    formData.append("category", selectedCategory);
    formData.append("heading", heading.trim());
    formData.append("description", description.trim());

    if (selectedCategory === "video") {
      formData.append("video_url", videoUrl.trim());
    } else {
      formData.append("file", file);
    }

    try {
      setUploading(true);

      await api.post("/materials/", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });

      setActiveCategory(selectedCategory);
      closeUploadForm();
      await fetchMaterials();
    } catch (err) {
      const responseData = err.response?.data;
      const message =
        typeof responseData === "string"
          ? responseData
          : responseData
            ? Object.entries(responseData)
                .map(
                  ([key, value]) =>
                    `${key}: ${Array.isArray(value) ? value.join(", ") : value}`,
                )
                .join(" ")
            : "Upload failed. Please check the details and try again.";

      setFormError(message);
    } finally {
      setUploading(false);
    }
  };

  const filteredMaterials = materials.filter(
    (material) => material.category === activeCategory,
  );

  const getMaterialLink = (material) => {
    if (material.category === "video") {
      return material.video_url;
    }

    return material.file;
  };

  const getMaterialAction = (material) => {
    if (material.category === "video") {
      return "Watch video";
    }

    return material.category === "ppt" ? "Open presentation" : "Open notes";
  };

  const goBack = () => {
    navigate("/modules", {
      state: { subject, branch, semester, role },
    });
  };

  return (
    <div className={styles.page}>
      <DashboardNavbar />

      <main className={styles.container}>
        <section className={styles.headingSection}>
          <p className={styles.eyebrow}>Study materials</p>
          <h1 className={styles.pageTitle}>
            {module?.name || module?.title || "Module materials"}
          </h1>

          <p className={styles.subtitle}>
            {subject?.name ? `${subject.name} · ` : ""}
            {branch?.name ? `${branch.name} · ` : ""}
            {semester?.name ||
              (semester?.number ? `Semester ${semester.number}` : "")}
          </p>

          <div className={styles.actions}>
            <button
              type="button"
              className={styles.backButton}
              onClick={goBack}
            >
              ← Back to modules
            </button>

            {isTeacher && (
              <button
                type="button"
                className={styles.uploadButton}
                onClick={() => setShowUploadForm(true)}
              >
                + Upload material
              </button>
            )}
          </div>
        </section>

        <section className={styles.materialSection}>
          <div
            className={styles.tabs}
            role="tablist"
            aria-label="Material categories"
          >
            {CATEGORIES.map((category) => (
              <button
                key={category.value}
                type="button"
                role="tab"
                aria-selected={activeCategory === category.value}
                className={`${styles.tab} ${
                  activeCategory === category.value ? styles.activeTab : ""
                }`}
                onClick={() => setActiveCategory(category.value)}
              >
                {category.label}
                <span className={styles.tabCount}>
                  {
                    materials.filter(
                      (material) => material.category === category.value,
                    ).length
                  }
                </span>
              </button>
            ))}
          </div>

          {loading ? (
            <div className={styles.statusMessage}>Loading materials…</div>
          ) : error ? (
            <div className={styles.errorMessage}>{error}</div>
          ) : filteredMaterials.length === 0 ? (
            <div className={styles.emptyState}>
              <div className={styles.emptyIcon}>📚</div>
              <h2>No {activeCategory.toUpperCase()} materials yet</h2>
              <p>
                {isTeacher
                  ? "Upload material for this category using the button above."
                  : "Your teacher has not added materials in this category yet."}
              </p>
            </div>
          ) : (
            <div className={styles.materialGrid}>
              {filteredMaterials.map((material) => {
                const link = getMaterialLink(material);

                return (
                  <article className={styles.materialCard} key={material.id}>
                    <div className={styles.cardTop}>
                      <span
                        className={`${styles.typeBadge} ${
                          styles[`${material.category}Badge`]
                        }`}
                      >
                        {material.category === "pdf"
                          ? "PDF"
                          : material.category === "ppt"
                            ? "PPT"
                            : "VIDEO"}
                      </span>

                      <span className={styles.cardIcon}>
                        {material.category === "pdf"
                          ? "📄"
                          : material.category === "ppt"
                            ? "📊"
                            : "▶"}
                      </span>
                    </div>

                    <h2 className={styles.materialTitle}>
                      {material.heading || "Untitled material"}
                    </h2>

                    <p className={styles.materialDescription}>
                      {material.description || "No description provided."}
                    </p>

                    <div className={styles.cardFooter}>
                      {link ? (
                        <a
                          className={styles.openButton}
                          href={link}
                          target="_blank"
                          rel="noreferrer"
                        >
                          {getMaterialAction(material)} <span></span>
                        </a>
                      ) : (
                        <span className={styles.unavailable}>
                          Link unavailable
                        </span>
                      )}

                      {material.uploaded_at && (
                        <span className={styles.uploadDate}>
                          {new Date(material.uploaded_at).toLocaleDateString()}
                        </span>
                      )}
                    </div>
                  </article>
                );
              })}
            </div>
          )}
        </section>
      </main>

      {showUploadForm && isTeacher && (
        <div className={styles.modalOverlay} onClick={closeUploadForm}>
          <section
            className={styles.modal}
            role="dialog"
            aria-modal="true"
            aria-labelledby="upload-title"
            onClick={(event) => event.stopPropagation()}
          >
            <div className={styles.modalHeader}>
              <div>
                <p className={styles.eyebrow}>Teacher upload</p>
                <h2 id="upload-title">Add study material</h2>
              </div>

              <button
                type="button"
                className={styles.closeButton}
                onClick={closeUploadForm}
                aria-label="Close upload form"
              >
                ×
              </button>
            </div>

            <form className={styles.uploadForm} onSubmit={handleUpload}>
              <label>
                Material type
                <select
                  value={selectedCategory}
                  onChange={(event) => {
                    setSelectedCategory(event.target.value);
                    setFormError("");
                  }}
                >
                  {CATEGORIES.map((category) => (
                    <option key={category.value} value={category.value}>
                      {category.label}
                    </option>
                  ))}
                </select>
              </label>

              <label>
                Title
                <input
                  type="text"
                  value={heading}
                  onChange={(event) => setHeading(event.target.value)}
                  placeholder="e.g. Unit 1 Notes"
                  required
                />
              </label>

              <label>
                Description
                <textarea
                  value={description}
                  onChange={(event) => setDescription(event.target.value)}
                  placeholder="Briefly describe this material"
                  rows="3"
                />
              </label>

              {selectedCategory === "video" ? (
                <label>
                  Video URL
                  <input
                    type="url"
                    value={videoUrl}
                    onChange={(event) => setVideoUrl(event.target.value)}
                    placeholder="https://..."
                    required
                  />
                </label>
              ) : (
                <label>
                  Select file
                  <input
                    type="file"
                    accept={
                      selectedCategory === "pdf"
                        ? ".pdf,application/pdf"
                        : ".ppt,.pptx,application/vnd.ms-powerpoint,application/vnd.openxmlformats-officedocument.presentationml.presentation"
                    }
                    onChange={(event) =>
                      setFile(event.target.files?.[0] || null)
                    }
                    required
                  />
                </label>
              )}

              {formError && <p className={styles.formError}>{formError}</p>}

              <div className={styles.formActions}>
                <button
                  type="button"
                  className={styles.cancelButton}
                  onClick={closeUploadForm}
                  disabled={uploading}
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  className={styles.uploadButton}
                  disabled={uploading}
                >
                  {uploading ? "Uploading…" : "Upload material"}
                </button>
              </div>
            </form>
          </section>
        </div>
      )}
    </div>
  );
}

export default Materials;
