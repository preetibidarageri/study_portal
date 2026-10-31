import styles from "./Hero.module.css";
import homeData from "../../data/home.json";

export default function Hero() {
  const { hero } = homeData;

  return (
    <section className={styles.hero}>
      <div className={styles.heroContent}>
        <h1>{hero.title}</h1>

        <p>{hero.description}</p>

        <a href={hero.button.url} className={styles.getStarted}>
          {hero.button.label}
        </a>
      </div>
    </section>
  );
}
