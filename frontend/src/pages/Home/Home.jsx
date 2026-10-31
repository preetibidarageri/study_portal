import Navbar from "../../components/Navbar/Navbar";
import Hero from "../../components/Hero/Hero";
import FeatureCard from "../../components/FeatureCard/FeatureCard";
import Footer from "../../components/Footer/Footer";

import styles from "./Home.module.css";
import homeData from "../../data/home.json";

function Home() {
  const { features } = homeData;

  return (
    <div className={styles.home}>
      <Navbar />

      <main>
        <Hero />

        <section className={styles.features} id="about">
          <h2>{features.heading}</h2>

          <div className={styles.featureContainer}>
            {features.items.map((item, index) => (
              <FeatureCard
                key={index}
                title={item.title}
                description={item.description}
              />
            ))}
          </div>
        </section>
      </main>

      <Footer />
    </div>
  );
}

export default Home;
