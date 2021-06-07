# %% Load imports
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import vuldataexplore as vde
import vuldataexplore.helpers as vdeh

# Get SARD Data and filter
df = vdeh.get_sard_df(verbose=1)

# %% Statistics to check
sns.set(font_scale=1.3)  # crazy big
fig, ax = plt.subplots(nrows=1, ncols=2, figsize=(18, 8))
sns.histplot(data=df, x="linesofcode", binwidth=50, ax=ax[0])
sns.histplot(data=df, x="num_markedlines", binwidth=1, ax=ax[1])
fig.savefig(vde.outputs_dir() / "sard_stats.png", dpi=300, bbox_inches="tight")

# %% Get tables
nfile_flaws = df.groupby("num_files_flawed").count()[["files"]].reset_index()
nfile_total = (
    df.groupby("num_files_total")
    .count()[["files"]]
    .sort_values("files", ascending=0)
    .reset_index()
)

# %% CWE Counting
cwe_df = pd.DataFrame([j for i in df.cwes for j in i], columns=["cwe"])
cwe_df["total"] = 1
cwe_df = cwe_df.groupby("cwe").count().sort_values("total", ascending=0)

# %% Markdown Tables
nfile_flaws.to_markdown()
nfile_total.to_markdown()
cwe_df.head(10).to_markdown()
cwe_df.to_markdown()

# --- Ideas ---
# How spread apart the individual lines are vs hunks
