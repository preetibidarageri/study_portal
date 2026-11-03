import styles from "./Footer.module.css";
import homeData from "../../data/home.json";

function Footer() {
  const { footer } = homeData;

  return (
    <footer className={styles.footer} id="contact">
      <p className={styles.copyright}>{footer.copyright}</p>
      <p className={styles.developer}>{footer.developer}</p>
    </footer>
  );
}

export default Footer;
