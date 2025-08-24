from pydriller import Repository
import pandas as pd

keywords = [
    "fixed", "bug", "fixes", "fix", "fix", "fixed", "fixes", "crash", 
    "solves", "resolves", "resolves", "issue", "regression", "fall back", 
    "assertion", "covertly", "reproducible", "stack-wanted", "steps-wanted", 
    "testcase", "failure", "fail", "npe", "npe", "except", "broken", 
    "differential testing", "error", "hang", "hang", "test fix", 
    "steps to reproduce", "crash", "assertion", "failure", "leak", 
    "stack trace", "heap overflow", "freeze", "problem", "problem", 
    "overflow", "overflow", "avoid", "avoid", "workaround", "workaround", 
    "break", "break", "stop"
]

bug_fix_commits = []
for commit in Repository('requests').traverse_commits():
    if any(keyword in commit.msg.lower() for keyword in keywords):
        bug_fix_commits.append({
            "Hash" : commit.hash,
            "Message" : commit.msg,
            "Hashes of parents" : commit.parents,
            "Is a merge commit?" : commit.merge,
            "List of modified files" : commit.modified_files
        })
df = pd.DataFrame(bug_fix_commits)
df.to_csv('bug_fix_commits.csv')