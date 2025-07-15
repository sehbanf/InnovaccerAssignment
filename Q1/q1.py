import pandas as pd
import re
import plotly.graph_objects as go
import numpy as np

# Load the data
conditions_df = pd.read_csv("C:\\Users\\ADMIN\\Desktop\\Q1\\synthea_sample_data_csv_latest\\conditions.csv", parse_dates=["START"], low_memory=False)
patients_df = pd.read_csv("C:\\Users\\ADMIN\\Desktop\\Q1\\synthea_sample_data_csv_latest\\patients.csv")

# Define pattern for CKD stages
pattern = r"chronic kidney disease stage \d|End-stage renal disease"
ckd_df = conditions_df[conditions_df["DESCRIPTION"].str.contains(pattern, case=False, na=False)].copy()

# Extract CKD stage from description
def extract_ckd_stage(desc):
    desc = desc.lower()
    if "stage" in desc:
        match = re.search(r"stage\s*(\d+)", desc)
        if match:
            return f"Stage {match.group(1)}"
    elif "end-stage renal disease" in desc:
        return "ESRD"
    return None

ckd_df["CKD_STAGE"] = ckd_df["DESCRIPTION"].apply(extract_ckd_stage)
ckd_df = ckd_df[ckd_df["CKD_STAGE"].notna()]

# Sort by patient and time
ckd_df = ckd_df.sort_values(by=["PATIENT", "START"])
ckd_df = ckd_df[["PATIENT", "START", "CKD_STAGE"]]

# Define CKD stage order
stage_order = ["Stage 1", "Stage 2", "Stage 3", "Stage 4", "Stage 5", "ESRD"]
stage_to_idx = {s: i for i, s in enumerate(stage_order)}

# Calculate transitions
transitions = []
for patient_id, group in ckd_df.groupby("PATIENT"):
    seen = {}
    for _, row in group.iterrows():
        stage = row["CKD_STAGE"]
        if stage not in seen:
            seen[stage] = row["START"]
    
    ordered = sorted(seen.items(), key=lambda x: stage_to_idx[x[0]])
    
    for i in range(len(ordered) - 1):
        from_stage, from_date = ordered[i]
        to_stage, to_date = ordered[i + 1]
        days = (to_date - from_date).days
        if days >= 0:
            transitions.append({
                "PATIENT": patient_id,
                "FROM": from_stage,
                "TO": to_stage,
                "DAYS": days
            })

transitions_df = pd.DataFrame(transitions)
merged_df = transitions_df.merge(patients_df, left_on="PATIENT", right_on="Id", how="left")

# Constructing full patient name
merged_df["PATIENT_NAME"] = (
    merged_df["FIRST"].fillna("") + " " +
    merged_df["MIDDLE"].fillna("") + " " +
    merged_df["LAST"].fillna("")
).str.replace(r'\s+', ' ', regex=True).str.strip()

merged_df = merged_df[["PATIENT", "PATIENT_NAME", "FROM", "TO", "DAYS"]]
# Summary of transitions
summary = merged_df.groupby(["FROM", "TO"])["DAYS"].agg(["count", "mean", "median"]).reset_index()
print("\n CKD Stage Transitions (per patient):")
print(merged_df.head())
print("\n Summary of Transitions:")
print(summary.head())
stages = ["Stage 1", "Stage 2", "Stage 3", "Stage 4", "Stage 5", "ESRD"]
stage_index = {stage: i for i, stage in enumerate(stages)}

# Filter transitions within valid stages
filtered = summary[summary["FROM"].isin(stages) & summary["TO"].isin(stages)].copy()

# Map source and target
filtered["source"] = filtered["FROM"].map(stage_index)
filtered["target"] = filtered["TO"].map(stage_index)

# hover text
filtered["label"] = (
    "From: " + filtered["FROM"] + "<br>" +
    "To: " + filtered["TO"] + "<br>" +
    "Patients: " + filtered["count"].astype(str) + "<br>" +
    "Avg Days: " + filtered["mean"].round(1).astype(str)
)


colors = [
    f"rgba(0, {int(255 - c)}, {int(c)}, 0.6)"
    for c in np.linspace(0, 255, len(filtered))
]

# Sankey diagram
fig = go.Figure(data=[go.Sankey(
    node=dict(
        pad=20,
        thickness=30,
        line=dict(color="gray", width=0.5),
        label=stages,
        color="lightsteelblue"
    ),
    link=dict(
        source=filtered["source"],
        target=filtered["target"],
        value=filtered["count"],
        label=filtered["label"],
        color=colors
    )
)])

fig.update_layout(
    title_text="CKD Stage Progression",
    font_size=13,
    plot_bgcolor="white",
    paper_bgcolor="white",
    margin=dict(l=20, r=20, t=50, b=20)
)

fig.show()