import Head from "next/head";
import { useState } from "react";
import { List, ListItem } from "@mui/material";
import { getChangelogData } from "../lib/changelog";
import Date from "../components/date";
import Layout from "../components/layout";
import Pagination from "../components/pagination";
import styles from "../styles/home.module.css";

export async function getStaticProps() {
  const changelogData = getChangelogData();
  return {
    props: {
      changelogData,
    },
  };
}

export default function Home({ changelogData }) {
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 5;

  const onPageChange = (page) => {
    setCurrentPage(page);
  };

  return (
    <Layout>
      <Head>
        <title>{`${changelogData.repositoryName} Changelog`}</title>
      </Head>
      <section className={styles.header}>
        <h1>{changelogData.repositoryName} Changelog</h1>
      </section>
      <section className={styles.description}>
        {changelogData.repositoryPath.startsWith("http") ? (
          <p>
            Viewing the change history for{" "}
            <a href={changelogData.repositoryPath}>
              {" "}
              {changelogData.repositoryName}
            </a>
          </p>
        ) : (
          <p>View the change history for {changelogData.repositoryName}</p>
        )}
      </section>
      <section className={styles.page_body}>
        <List>
          {changelogData.history.map((item, index) => {
            if (
              index < currentPage * pageSize &&
              index >= (currentPage - 1) * pageSize
            ) {
              const splitItem = item.split("\n");
              const date = splitItem[0];
              const summary = splitItem.length > 1 ? splitItem[1] : "";
              const explanation = splitItem.length > 2 ? splitItem[2] : "";

              return (
                <ListItem
                  divider={
                    index === currentPage * pageSize - 1 ||
                    index === changelogData.history.length - 1
                      ? false
                      : true
                  }
                >
                  <section>
                    <small>
                      <Date dateString={date} />
                    </small>
                    <h4> {summary} </h4>
                    <p>{explanation}</p>
                  </section>
                </ListItem>
              );
            }
          })}
        </List>
      </section>
      <section>
        <Pagination
          totalPages={Math.ceil(changelogData.history.length / pageSize)}
          currentPage={currentPage}
          setCurrentPage={setCurrentPage}
        />
      </section>
    </Layout>
  );
}
