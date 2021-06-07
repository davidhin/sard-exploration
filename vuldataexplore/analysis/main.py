# %%
import xml.etree.ElementTree as ET

import pandas as pd
from tqdm import tqdm

# %%
tree = ET.parse("SARD_testcaseinfo.xml")
root = tree.getroot()

# %%
test_id_flaws = []
for child in tqdm(root):
    testid = child.attrib["id"]
    flaws = [i.attrib for i in child.findall("./file/flaw")]
    test_id_flaws.append([testid, flaws, len(flaws)])

# %%
df = pd.DataFrame(test_id_flaws, columns=["testid", "flaws", "numflaws"])

# %%

df.sort_values("numflaws")
# %%
df[df["testid"] == "187"]["numflaws"]

df[df["testid"] == "187"]["flaws"]
