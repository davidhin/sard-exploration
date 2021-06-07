"""Helper functions for exploring datasets."""
import xml.etree.ElementTree as ET

import pandas as pd
import vuldataexplore as vde
from tqdm import tqdm


def get_file_loc(filepath):
    """Get number of non-blank lines of a file.

    Args:
        filepath (str): Path to file
    """
    with open(filepath, errors="ignore") as f:
        locs = len([i for i in f.readlines() if len(i.strip()) > 0])
    return locs


def get_sard_df(maxlocs=1000, maxmark=15, verbose=0):
    """Get SARD manifest and filter accordingly.

    Args:
        maxlocs (int, optional): Filter all test cases with more LOCs than this. Defaults to 1000.
        maxmark (int, optional): Filter all test cases with more marked lines than this. Defaults to 15.
        verbose (int, optional): Verbosity. Defaults to 0.
    """
    tree = ET.parse(vde.external_dir() / "full_manifest.xml")
    root = tree.getroot()
    test_id_flaws = []
    count_sard_total = len(root)
    count_deprecated = 0
    count_lang = 0
    count_nomarked = 0
    count_hasfix = 0

    for child in tqdm(root):
        status = child.attrib["status"]
        testid = child.attrib["id"]
        lang = child.attrib["language"]

        # FILTER: Deprecated
        if status == "Deprecated":
            count_deprecated += 1
            continue

        # FILTER: Programming language
        if lang not in ["C", "C++"]:
            count_lang += 1
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
            # FILTER: ignore header files
            flaws = [i for i in flaws if i["path"][-2:] != ".h"]
            if len(flaws) > 0:
                markedlines += flaws

        # FILTER: At least one flawed/mixed line
        if len(markedlines) == 0:
            count_nomarked += 1
            continue

        # FILTER: No fixlines (good cases)
        num_fixlines = len([i for i in markedlines if i["linetag"] == "fix"])
        if num_fixlines > 0:
            count_hasfix += 1
            continue

        # Manually calculate number of files with marked lines
        unique_paths = set([i["path"] for i in markedlines])
        num_files_flawed = len(unique_paths)

        # Get total LOCs for files with marked lines.
        locs = [
            get_file_loc(vde.external_dir() / "testcases" / i) for i in unique_paths
        ]

        test_id_flaws.append(
            {
                "testid": testid,
                "files": markedlines,
                "num_markedlines": len(markedlines),
                "num_flawlines": len(
                    [i for i in markedlines if i["linetag"] == "flaw"]
                ),
                "num_mixedlines": len(
                    [i for i in markedlines if i["linetag"] == "mixed"]
                ),
                "num_fixlines": num_fixlines,
                "lang": lang,
                "num_files_total": len(child.findall("./file")),
                "num_files_flawed": num_files_flawed,
                "cwes": [i["name"] for i in markedlines],
                "status": status,
                "filepaths": list(unique_paths),
                "linesofcode": sum(locs),
            }
        )
    df = pd.DataFrame.from_records(test_id_flaws)
    fdf = df[df.linesofcode < maxlocs]
    count_locfilter = len(fdf)
    fdf = fdf[fdf.num_markedlines < maxmark]
    count_linenofilter = len(fdf)

    if verbose > 0:
        printstr = ""
        printstr += f"SARD Total: {count_sard_total}\n"
        count_sard_total -= count_deprecated
        printstr += f"Removed deprecated: {count_sard_total}\n"
        count_sard_total -= count_lang
        printstr += f"Removed non-C/C++: {count_sard_total}\n"
        count_sard_total -= count_nomarked
        printstr += f"Removed tests with no marked lines: {count_sard_total}\n"
        count_sard_total -= count_hasfix
        printstr += f"Removed tests with fixed lines (good cases): {count_sard_total}\n"
        printstr += f"Removed tests with > {maxlocs} loc: {count_locfilter}\n"
        printstr += f"Removed tests with >={maxmark} marked lines: {count_linenofilter}"
        print(printstr)

    return fdf
