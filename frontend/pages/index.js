import Head from "next/head";
import { getChangelogData } from "../lib/changelog";
import Date from "../components/date";

export async function getStaticProps() {
  const changelogData = getChangelogData();
  return {
    props: {
      changelogData,
    },
  };
}

export default function Home({ changelogData }) {
  const repository = "iTinerary";
  return (
    <div>
      <Head>
        <title>{repository} Changelog</title>
      </Head>
      <section>
        <h1>{repository} Changelog</h1>
      </section>
      <section>
        <p> View the change history for {repository}</p>
        {changelogData.fileContents.map((item) => {
          const splitItem = item.split("\n");
          const date = splitItem[0];
          const summary = splitItem.length > 1 ? splitItem[1] : "";
          const explanation = splitItem.length > 2 ? splitItem[2] : "";

          return (
            <section>
              <Date dateString={date} />
              <h4> {summary} </h4>
              <p> {explanation} </p>
            </section>
          );
        })}
      </section>
    </div>
  );
}
