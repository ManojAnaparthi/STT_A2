import pandas as pd
from pydriller import Repository
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

# Load CommitPredictorT5 Model

MODEL_NAME = "mamiksik/CommitPredictorT5"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)

def predict_fix_type(diff_text, max_length=64):
    if not diff_text.strip():
        return "N/A"
    inputs = tokenizer(diff_text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model.generate(**inputs, max_length=max_length)
    return tokenizer.decode(outputs[0], skip_special_tokens=True)

# Load Bug-Fix Commits from Part (c)
bug_fix_df = pd.read_csv("bug_fix_commits.csv")
bug_commit_hashes = set(bug_fix_df["Hash"])

# Traverse Repository (local copy)
repo_path = "requests"
rows = []

for commit in Repository(repo_path).traverse_commits():
    if commit.hash not in bug_commit_hashes:
        continue   # only process bug-fixing commits

    for mod in commit.modified_files:
        diff = mod.diff if mod.diff else ""

        # Store entire source code before and after
        source_code_before = mod.source_code_before if mod.source_code_before else ""
        source_code_after = mod.source_code if mod.source_code else ""

        # LLM inference
        llm_pred = predict_fix_type(diff)

        rows.append({
            "Hash": commit.hash,
            "Message": commit.msg,
            "Filename": mod.filename,
            "Source_Code_Before": source_code_before,
            "Source_Code_After": source_code_after,
            "Diff": diff,
            "LLM_Inference": llm_pred,
            "Developer_Message": commit.msg,
            "Rectified Message": ""  # placeholder for part (e,f)
        })

# Save to DataFrame + CSV
diff_df = pd.DataFrame(rows)
diff_df.to_csv("diff_analysis.csv", index=False)

print(f"Saved {len(diff_df)} file-level bug-fix records to diff_analysis.csv")
