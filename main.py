import argparse
import subprocess
from contextlib import closing

from openpyxl import load_workbook

import bundle
import fulfilment
from schema import SchemaField, SchemaEntity, Schema
from xml_builder import XMLBuilder

## ARGS
parser = argparse.ArgumentParser(
    description="Process bundled product definitions spreadsheet"
)

parser.add_argument("-i", "--import", dest="import_file", required=True, help="import file")
parser.add_argument("-e", "--export", dest="export_file", required=True, help="export file")

args = parser.parse_args()

subprocess.run("cls", shell=True)
subprocess.run(f"@echo Using import file {args.import_file}", shell=True)
subprocess.run(f"@echo export to {args.export_file}", shell=True)

with open(args.export_file, "w", encoding="utf-8") as f:
    # xml = fulfilment.Fulfilment().process_work_book(args.import_file).process_entities()
    xml = bundle.Bundle().process_work_book(args.import_file).process_entities()
    f.write(xml.text())
