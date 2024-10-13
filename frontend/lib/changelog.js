import fs from "fs";
import path from "path";
const changelogDirectory = path.join(process.cwd(), "/changelog");

export function getChangelogData() {
  const fileName = "changelog";
  const fullPath = path.join(changelogDirectory, fileName);

  const fileContents = fs.readFileSync(fullPath, "utf8").trim().split("\n\n");
  return {
    fileContents,
  };
}
