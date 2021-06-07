# %%
import xml.etree.ElementTree as ET
from collections import Counter

import pandas as pd
import vuldataexplore as vde
from tqdm import tqdm

tree = ET.parse(vde.external_dir() / "full_manifest.xml")
root = tree.getroot()

# %%
test_id_flaws = []
for child in tqdm(root):
    testid = child.attrib["id"]
    lang = child.attrib["language"]
    num_files = child.attrib["numberOfFiles"]

    # FILTER: Programming language
    if lang not in ["C", "C++"]:
        continue

    suslines = []
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
            suslines += flaws

    # FILTER: At least one flawed/mixed line
    if len(suslines) == 0:
        continue

    test_id_flaws.append(
        {
            "testid": testid,
            "files": suslines,
            "num_suslines": len(suslines),
            "lang": lang,
            "num_files": num_files,
            "cwes": [i["name"] for i in suslines],
        }
    )
df = pd.DataFrame.from_records(test_id_flaws)
