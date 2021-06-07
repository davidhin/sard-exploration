# %%
import xml.etree.ElementTree as ET

import pandas as pd
import vuldataexplore as vde
from tqdm import tqdm

tree = ET.parse(vde.external_dir() / "full_manifest.xml")
root = tree.getroot()

# %%
test_id_flaws = []
for child in tqdm(root):
    status = child.attrib["status"]
    testid = child.attrib["id"]
    lang = child.attrib["language"]

    # FILTER: Deprecated
    if status == "Deprecated":
        continue

    # FILTER: Programming language
    if lang not in ["C", "C++"]:
        continue

    # Extract list of flawed/mixed lines.
    markedlines = []
    for testcasefile in child.findall("./file"):
        flaws = []
        for fileline in testcasefile:
            flaws += [
                {
                    **testcasefile.attrib,
                    **fileline.attrib,
                    **{"linetag": fileline.tag},
                }
            ]
        # FILTER: flawed/mixed lines with line_number == 0
        flaws = [i for i in flaws if i["line"] != "0"]
        if len(flaws) > 0:
            markedlines += flaws

    # FILTER: At least one flawed/mixed line
    if len(markedlines) == 0:
        continue

    # FILTER: No fixlines (good cases)
    num_fixlines = len([i for i in markedlines if i["linetag"] == "fix"])
    if num_fixlines > 0:
        continue

    test_id_flaws.append(
        {
            "testid": testid,
            "files": markedlines,
            "num_markedlines": len(markedlines),
            "num_flawlines": len([i for i in markedlines if i["linetag"] == "flaw"]),
            "num_mixedlines": len([i for i in markedlines if i["linetag"] == "mixed"]),
            "num_fixlines": num_fixlines,
            "lang": lang,
            "num_files": len(child.findall("./file")),
            "cwes": [i["name"] for i in markedlines],
            "status": status,
        }
    )
df = pd.DataFrame.from_records(test_id_flaws)

df[df.testid == "91116"]

# %% Statistics to check
# How spread apart the individual lines are vs hunks
# How long each of the files are
# Distribution of number of files
