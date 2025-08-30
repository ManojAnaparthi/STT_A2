import pandas as pd

SPECIFIC_TERMS = {
    "error", "crash", "typo", "parser", "memory", "api", "login",
    "auth", "cleanup", "handling"
}

GENERIC_WORDS = {
    "fixed", "bug", "fixes", "fix", "crash", "solves", "resolves", "issue",
    "regression", "fall back", "assertion", "covertly", "reproducible",
    "stack-wanted", "steps-wanted", "testcase", "failure", "fail", "npe",
    "except", "broken", "differential testing", "error", "hang",
    "test fix", "steps to reproduce", "leak", "stack trace",
    "heap overflow", "freeze", "problem", "overflow", "avoid",
    "workaround", "break", "stop"
}

def is_generic(msg):
    words = msg.lower().split()
    return len(words) <= 3 or all(w in GENERIC_WORDS for w in words)

def rectified_message(dev_msg, llm_msg, filename):
    if not isinstance(dev_msg, str): dev_msg = ""
    if not isinstance(llm_msg, str): llm_msg = ""
    if not isinstance(filename, str): filename = ""

    dev_msg, llm_msg = dev_msg.strip(), llm_msg.strip()
    source = None

    # Case 1: both empty
    if not dev_msg and not llm_msg:
        chosen, source = f"Bug fix in {filename}", "Fallback"

    # Case 2: only one exists
    elif dev_msg and not llm_msg:
        chosen, source = dev_msg, "Developer"
    elif llm_msg and not dev_msg:
        chosen, source = llm_msg, "LLM"

    else:
        dev_lower, llm_lower = dev_msg.lower(), llm_msg.lower()

        # Case: duplicates
        if dev_lower == llm_lower or dev_lower in llm_lower or llm_lower in dev_lower:
            if len(dev_msg) >= len(llm_msg):
                chosen, source = dev_msg, "Developer"
            else:
                chosen, source = llm_msg, "LLM"

        # Case: generic vs descriptive
        elif is_generic(dev_msg) and not is_generic(llm_msg):
            chosen, source = llm_msg, "LLM"
        elif is_generic(llm_msg) and not is_generic(dev_msg):
            chosen, source = dev_msg, "Developer"

        # Case: specific terms preference
        elif any(term in dev_lower for term in SPECIFIC_TERMS) and not any(term in llm_lower for term in SPECIFIC_TERMS):
            chosen, source = dev_msg, "Developer"
        elif any(term in llm_lower for term in SPECIFIC_TERMS) and not any(term in dev_lower for term in SPECIFIC_TERMS):
            chosen, source = llm_msg, "LLM"

        # Case: neither dominates → merge
        else:
            chosen, source = f"{dev_msg} – {llm_msg}", "Merged"

    # Ensure filename context
    if filename and filename.lower() not in chosen.lower():
        chosen = f"{chosen} ({filename})"

    return chosen, source


# -----------------------------
# Load data
df = pd.read_csv("diff_analysis.csv")

# Drop the existing empty "Rectified Message" column if it exists
if "Rectified_Message" in df.columns:
    df = df.drop("Rectified Message", axis=1)

# Apply rectifier
results = df.apply(
    lambda row: rectified_message(
        row.get("Message", ""),
        row.get("LLM_Inference", ""),
        row.get("Filename", "")
    ),
    axis=1
)

df["Rectified_Message"] = [r[0] for r in results]
df["Source"] = [r[1] for r in results]

# Save rectified CSV
df.to_csv("diff_analysis_rectified_sample.csv", index=False)

# Compute RQs
rq1 = (df["Source"] == "Developer").mean() * 100
rq2 = (df["Source"] == "LLM").mean() * 100
rq3 = (df["Source"].isin(["Merged", "Fallback"])).mean() * 100

print("==== Hit Rates (% by Source) ====")
print(df["Source"].value_counts(normalize=True) * 100)

print("\n==== Research Question Results ====")
print(f"RQ1 (Developer precision): {rq1:.2f}%")
print(f"RQ2 (LLM precision): {rq2:.2f}%")
print(f"RQ3 (Rectifier improvement): {rq3:.2f}%")