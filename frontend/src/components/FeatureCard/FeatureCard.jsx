import styles from "./FeatureCard.module.css";

function FeatureCard({ title, description }) {
  return (
    <div className={styles.featureCard}>
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

export default FeatureCard;
