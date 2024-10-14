from git.exc import InvalidGitRepositoryError, NoSuchPathError
from langchain.chains import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEndpoint
import sys
import os
import shutil
from dotenv import load_dotenv
import argparse
os.environ["GIT_PYTHON_REFRESH"] = "quiet"
from git import Repo
import time
import string

load_dotenv()

class LLMRunner:
    def __init__(self, template, input_variables, llm_repo_id, max_new_tokens=128, temperature=.5):
        self.template = template
        self.prompt = PromptTemplate(template=self.template, input_variables=input_variables)
        self.llm_repo_id = llm_repo_id
        self.llm = HuggingFaceEndpoint(
            repo_id=self.llm_repo_id,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
        )
        self.llm_chain = self.prompt | self.llm

class RepoRunner():
    def __init__(self):
        self.cloned_path = None

    def remote_repo(self, url, to_path):
        '''
        Initialize repo using a remote repository
        Parmaters:
            url: string
                remote repository URL
            to_path: string
                location to save temporary cloned repo (deleted on cleanup)
        '''
        try:
            self.repo = Repo.clone_from(
                url, to_path=to_path
            )
            self.cloned_path = to_path
            self.repo_path = url
        except:
            print("Failed to clone repo")
            sys.exit(1)

    def local_repo(self, repo_path):
        '''
        Initialize repo using a local repository
        Parameters:
            repo_path: string
                path to local directory containing .git folder
        '''
        try:
            self.repo = Repo(repo_path)
        except InvalidGitRepositoryError:
            print("No git repository found at that location")
            sys.exit(1)
        self.repo_path = repo_path

    def generate_changelog(self, llm_runner, max_count, after, before):
        '''
        Pass git commit history and file diffs to LLM and generate changelog.
        Parameters:
            llm_runner: LLM_Runner
                wrapper class for LLMChain
            max_count: int
                maximum number of commits to parse
            after: string (format MM.DD.YYYY)
                only parse commits after given date
            before: string (format MM.DD.YYYY)
                only parse commits before given date
        '''
        with open("./changelog", "w") as f:
            f.write(self.repo_path + "\n\n")
            commits = list(self.repo.iter_commits("main", max_count=max_count, after=after, before=before))
            for i in range(len(commits) - 1):
                commit_message = commits[i].message
                commit_date = commits[i].committed_date
                formatted_time = time.strftime("%Y-%m-%d", time.gmtime(commit_date))
                diff_text = ""
                for diff in commits[i].diff(commits[i + 1]):
                    match diff.change_type:
                        case "M":
                            diff_text += "Modified "
                            diff_text += diff.a_path + "\n"
                        case "A":
                            diff_text += "Added "
                            diff_text += diff.a_path + "\n"
                        case "D":
                            diff_text += "Deleted "
                            diff_text += diff.a_path + "\n"
                        case "R":
                            diff_text += "Renamed "
                            diff_text += diff.a_path + " to " + diff.b_path + "\n"
                        case "C":
                            diff_text += "Copied\n"
                            diff_text += diff.a_path + "\n"

                response = llm_runner.llm_chain.invoke({"commit_message": commit_message, "diff": diff_text})
                response = response.split("\n")
                response = list(map(cleanup_output, response))
                response = [line for line in response if line]
                if len(response) >= 2:
                    f.write(formatted_time + "\n")
                    f.write(response[0] + "\n")
                    f.write(" ".join(response[1:]) + "\n\n")


    def cleanup(self):
        '''
        Delete cloned repository
        '''
        if self.cloned_path:
            shutil.rmtree(self.cloned_path)

def cleanup_output(x):
    '''
    Reomve extraneous LLM output
    Parameters:
        x: string
            text returned by LLM for a single commit
    Returns:
        string
    '''
    x = x.lstrip(string.punctuation)
    x = x.replace("Summary:", "")
    x = x.replace("Changes:", "")
    x = x.replace("Explanation", "")
    return x.strip()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", help="URL to clone repo from")
    parser.add_argument("--repo_path", help="Path to local repo")
    parser.add_argument("--llm_repo_id", help="Repo id of HuggingFace LLM", default="mistralai/Mistral-7B-Instruct-v0.2")
    parser.add_argument("--max_count", help="Only parse a given number of commits", default=20)
    parser.add_argument("--after", help="Only parse commits after given date. Format: MM.DD.YYYY", default=None)
    parser.add_argument("--before", help="Only parse commits before given date. Format: MM.DD.YYYY", default=None)
    args = parser.parse_args()

    if args.url and args.repo_path:
        print("You can only specify a remote repo or a local repo")
        sys.exit(1)

    if not args.url and not args.repo_path:
        print("You must specify either a remote repo or a local repo")
        sys.exit(1)

    repo_runner = RepoRunner()
    to_path="./cloned_repo"
    if args.url:
        repo_runner.remote_repo(args.url, to_path)
    elif args.repo_path:
        repo_runner.local_repo(args.repo_path)

    template = """
    commit message: {commit_message} | diff: {diff}

    Given the commit message and the diff, your task is to generate a short summary of the commit.
    First provide a short (10 words or less) high-level summary of the changes. Then provide a
    more detailed (2-5 sentences) explanation. Make sure to mention which files were changed,
    the reason for the changes, and how the changes might impact a user. Assume the user has some
    knowledge of the project and its technologies. Do not explicitly mention the commit message or
    the diff. Use proper spelling and grammar, and only write in complete sentences.
    Write in the tone of a software engineer. Write confidently - avoid words like 'likely' and 'may.
    Write your response in the following format and make sure to use full sentences:

    Summary:
        high-level summary of the changes
    Changes:
        2-5 sentence explanation
    """

    input_variables=["commit_message", "diff"]

    llm_runner = LLMRunner(template, input_variables, args.llm_repo_id)

    repo_runner.generate_changelog(llm_runner, args.max_count, args.after, args.before)
    repo_runner.cleanup()
