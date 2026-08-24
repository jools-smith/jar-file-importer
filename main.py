import argparse
import subprocess
from contextlib import closing

import openpyxl
from openpyxl import load_workbook

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

# MAIN

product_name = SchemaField("productName")
product_version = SchemaField("productVersion")
state = SchemaField("state")
feature_name = SchemaField("featureName")
feature_version = SchemaField("featureVersion")
feature_count = SchemaField("featureCount")
skus = SchemaField("skus", False)
bundles = SchemaField("bundles", False)

## schema definition
bundle_schema = Schema(
    name="bundle",
    fields=[
        product_name,
        product_version,
        state,
        feature_name,
        feature_version,
        feature_count,
        skus,
        bundles])

def process_work_book() -> list[SchemaEntity]:
    current = None
    local_entities: list[SchemaEntity] = []

    with closing(load_workbook(args.import_file, read_only=True)) as work_book:
        work_sheet = work_book.active

        headers = bundle_schema.validate_sheet(work_sheet)
        ##DEBUG
        print(f'columns \n\t{"\n\t".join(headers)}')

        # Process data rows
        for row_num, row in enumerate(
                work_sheet.iter_rows(min_row=2, values_only=True),
                start=2):

            record = dict(zip(headers, row))
            # print(record)
            if not Schema.row_is_empty(record):
                ## not a blank row
                if current is None or (
                        record[product_name.name] and record[product_name.name] != current.get_value(product_name)):

                    current = bundle_schema.create_entity(record, row_num)

                    local_entities.append(current)
                else:
                    current.validate_matching(record, row_num)

                if record[skus.name]:
                    current.append_value(skus, record[skus.name])

                if record[bundles.name]:
                    current.append_value(bundles, record[bundles.name])

        return local_entities


## generate XML
entities = process_work_book()

xml = XMLBuilder()
xml.initialize("products")

for ent in entities:
    print(ent.get_value(product_name))

    xml.push_tag("product")
    xml.push_cdata("productName", ent.get_value(product_name))
    xml.push_cdata("version", ent.get_value(product_version))
    xml.push_cdata("state", ent.get_value(state))
    xml.push_tags("features", "feature", "primaryKeys")
    xml.push_cdata("name", ent.get_value(feature_name))
    xml.push_cdata("version", ent.get_value(feature_version))
    xml.pop_tag("primaryKeys")
    xml.push_cdata("count", ent.get_value(feature_count))
    xml.pop_tag("features")
    xml.push_tags("categoryAttributes")

    if ent.has_value(bundles):
        xml.push_tags("categoryAttribute")
        xml.push_cdata("attributeName", "BUNDLES")
        xml.push_cdata("attributeValue", ";".join(ent.get_value(bundles)))
        xml.pop_tag("categoryAttribute")

    if ent.has_value(skus):
        xml.push_tags("categoryAttribute")
        xml.push_cdata("attributeName", "SKUS")
        xml.push_cdata("attributeValue", ";".join(ent.get_value(skus)))
        xml.pop_tag("categoryAttribute")

    xml.pop_tag("product")

xml.pop_tag("products")

with open(args.export_file, "w", encoding="utf-8") as f:
    f.write(xml.text())
