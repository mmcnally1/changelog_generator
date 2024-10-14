## Changelog Generator and Frontend Display
This project consists of 2 parts. The first part is a tool for generating changelogs
using an LLM. The tool is implemented in python and uses the HuggingFace API for LLM querying.
Given either a local directory containing a .git folder or the URL for a github repository,
the changelog generator compiles the commit and diff history and queries an LLM for a summary and
description of the changes and writes the output to a file called "changelog".
The second part is a frontend for displaying a changelog. The changelog should be placed in the
`frontend/changelog` directory. The frontend is implemented using Next.js, and displays the content
of the changelog in a browser (it is not deployed so it will run on localhost).

## Running the programs
### Changelog Generator
A HuggingFace API key is required to run the changelog generator. They are free to create and use, and
instructions for creating one can be found [here] (https://www.geeksforgeeks.org/how-to-access-huggingface-api-key/). Once you have
your API key, store it in a `.env` file in the changelog_tool folder under the variable name HF_TOKEN.
Then you can install the dependencies (the dependencies may take 10-15 to install, and Python >= 3.10
is required):
```
pip install -r requirements.txt
```
and run the program:
#### On a github repo
```
python3 changelog_generator.py --url <your repo url>
```
#### On a local repo
```
python3 changelog_generator.py --repo_path <your repo url>
```
You can also pass the following optional arguments:
`--llm_repo_id` if you would like to choose which LLM to use (your own or one that is publicly hosted on HuggingFace)
`--max_count` if you would like to set a limit on the number of commits to parse (note that the LLM is invoked for each commit
and HuggingFace limits free users to 1000 queries per day)
`--after` only parse commits after a given date (format MM.DD.YYYY)
`--before` only parse commits before a given date (format MM.DD.YYYY)
