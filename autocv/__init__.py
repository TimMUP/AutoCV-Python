import os
import json
import glob
import re
import timeit
import time
import pylumber as pl

from docx import Document
from dotenv import dotenv_values


def json_to_dict(json_path: str):
    with open(json_path) as f:
        return json.load(f)

def csv_to_dict(file_path: str):
    tempDict = {}
    with open(file_path) as csvFile:
        for line in csvFile:
            # Get index of first comma
            firstComma = line.find(",")
            tempDict[line[:firstComma]] = line[firstComma+1:].strip()

    return tempDict

# Credits to Scanny for the code below:
def paragraph_replace_text(paragraph, regex, replace_str):
    """Return `paragraph` after replacing all matches for `regex` with `replace_str`.

    `regex` is a compiled regular expression prepared with `re.compile(pattern)`
    according to the Python library documentation for the `re` module.
    """
    # --- a paragraph may contain more than one match, loop until all are replaced ---
    while True:
        text = paragraph.text
        match = regex.search(text)
        if not match:
            break

        # --- when there's a match, we need to modify run.text for each run that
        # --- contains any part of the match-string.
        runs = iter(paragraph.runs)
        start, end = match.start(), match.end()

        # --- Skip over any leading runs that do not contain the match ---
        for run in runs:
            run_len = len(run.text)
            if start < run_len:
                break
            start, end = start - run_len, end - run_len

        # --- Match starts somewhere in the current run. Replace match-str prefix
        # --- occurring in this run with entire replacement str.
        run_text = run.text
        run_len = len(run_text)
        run.text = "%s%s%s" % (run_text[:start], replace_str, run_text[end:])
        end -= run_len  # --- note this is run-len before replacement ---

        # --- Remove any suffix of match word that occurs in following runs. Note that
        # --- such a suffix will always begin at the first character of the run. Also
        # --- note a suffix can span one or more entire following runs.
        for run in runs:  # --- next and remaining runs, uses same iterator ---
            if end <= 0:
                break
            run_text = run.text
            run_len = len(run_text)
            run.text = run_text[end:]
            end -= run_len

    # --- optionally get rid of any "spanned" runs that are now empty. This
    # --- could potentially delete things like inline pictures, so use your judgement.
    # for run in paragraph.runs:
    #     if run.text == "":
    #         r = run._r
    #         r.getparent().remove(r)

    return paragraph  


class template():
    def __init__(self, lut: dict, template: str, output_dir: str = "output"):
        # Open and parse json config file:
        self.LOOKUP = lut
        self.TEMPLATE = template
        # Check to see if output directory exists
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        self.OUTPUT_DIR = output_dir

    def find_and_replace_single(self, config: json):
        # Returns: Docx Document
        tempConfig = json_to_dict(config)
        tempDocx = Document(self.TEMPLATE)

        # Do reactjs replacement 
        reMFR = re.compile(r"\{([^}]*)\}")
        for key, value in tempConfig.items():
            reMFR = re.compile(r"\{" + key + r"\}")
            for paragraph in tempDocx.paragraphs:
                paragraph = paragraph_replace_text(paragraph, reMFR, value)
        # Save the edited document within output directory
        tempDocx.save(f"{self.OUTPUT_DIR}/{tempConfig['UID']}.docx")
        
        
    
    def find_and_replace_group(self, config_path: str):
        print(config_path)

    def __exit__(self):
        print("Exiting...")