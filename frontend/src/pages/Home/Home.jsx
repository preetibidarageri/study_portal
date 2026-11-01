import Navbar from "../../components/Navbar/Navbar";
import Footer from "../../components/Footer/Footer";
import styles from "./Home.module.css";
import homeData from "../../data/home.json";

function HoverLetters({ text }) {
  return (
    <>
      {text.split("").map((letter, index) => (
        <span
          className={styles.hoverLetter}
          key={`${letter}-${index}`}
          style={{ "--letter-index": index }}
        >
          {letter === " " ? "\u00A0" : letter}
        </span>
      ))}
    </>
  );
}

export default function Home() {
  return (
    <div className={styles.home}>
      <Navbar />

      <main>
        <section className={styles.hero}>
          <div className={styles.heroContent}>
            <p className={styles.eyebrow}>SKSV STUDY MATERIAL PORTAL</p>

            <h1>
              <HoverLetters text={homeData.hero.title} />
            </h1>

            <p className={styles.heroDescription}>
              {homeData.hero.description}
            </p>

            <a className={styles.getStarted} href={homeData.hero.button.url}>
              {homeData.hero.button.label}
            </a>
          </div>
        </section>

        <section className={styles.features}>
          <div className={styles.sectionHeader}>
            <h2>{homeData.features.heading}</h2>
          </div>

          <div className={styles.featureContainer}>
            {homeData.features.items.map((feature, index) => (
              <article className={styles.featureCard} key={feature.title}>
                <span className={styles.cardNumber}>
                  {String(index + 1).padStart(2, "0")}
                </span>
                <h3>{feature.title}</h3>
                <p>{feature.description}</p>
              </article>
            ))}
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}
