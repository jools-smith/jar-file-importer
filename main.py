import argparse
import subprocess
from typing import Any
from pathlib import Path
from IPython.display import clear_output

import bundle
import fulfilment

## ARGS
parser = argparse.ArgumentParser(
  description="Process bundled product definitions spreadsheet"
)

parser.add_argument("-i", "--import",
  dest="import_file",
  required=True,
  help="import file"
)

parser.add_argument("-o", "--output",
  dest="output_file",
  required=True,
  help="output file"
)

parser.add_argument("-t", "--type",
  dest="type",
  choices=["fulfilment", "fulfillment", "bundle"],
  required=True,
  default="bundle",
  help="fulfilment | fulfillment | bundle"
)

args = parser.parse_args()

clear_output(wait=True)
subprocess.run(f"@echo Using import file {args.import_file}", shell=True)
subprocess.run(f"@echo export to {args.output_file}", shell=True)

xml = list[str]

if args.type == "bundle":
  xml = bundle.Bundle().process_work_book(args.import_file).process_entity_groups(200)
else:
  xml = fulfilment.Fulfilment().process_work_book(args.import_file).process_entity_groups(20)

for i, content in enumerate(xml, start=1):
  Path(f"{args.output_file}_{i}.xml").write_text(content, encoding="utf-8")
