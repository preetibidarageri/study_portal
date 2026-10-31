import styles from "./Footer.module.css";
import homeData from "../../data/home.json";

function Footer() {
  const { footer } = homeData;

  return (
    <footer className={styles.footer} id="contact">
      <p>{footer.copyright}</p>
    </footer>
  );
}

export default Footer;
