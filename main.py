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

## MAIN
# product_name = SchemaField("productName")
# product_version = SchemaField("productVersion")
# state = SchemaField("state")
# feature_name = SchemaField("featureName")
# feature_version = SchemaField("featureVersion")
# feature_count = SchemaField("featureCount")
# skus = SchemaField("skus", False)
# bundles = SchemaField("bundles", False)

## schema definition
# bundle_schema = Schema(
#     name="bundle",
#     fields=[
#         product_name,
#         product_version,
#         state,
#         feature_name,
#         feature_version,
#         feature_count,
#         skus,
#         bundles])
#
# ## schema definition
# fulfilment_id = SchemaField("fulfillmentId")
# activation_id = SchemaField("activationId")
# activation_count = SchemaField("activationCount")
# overdraft_count = SchemaField("overdraftCount", False)
# start_date = SchemaField("startDate")
#
# att_comment = SchemaField("Comment", False)
# att_hcltech_email = SchemaField("HCLTech_Email", False)
# att_hcltech_representative = SchemaField("HCLTech_Representative", False)
# att_order_number = SchemaField("Order_Number", False)
# att_product_name = SchemaField("Product_Name", False)
# att_product_version = SchemaField("Product_Version", False)
# att_sales_contact_email = SchemaField("Sales_Contact_Email", False)
#
# fulfilment_date_time = SchemaField("fulfillDateTime")
# license_file_definition_name = SchemaField("licenseDefinitionName")
# license = SchemaField("license")
# license_filename = SchemaField("licfilename")
#
# fulfilment_schema = Schema(
#     name="fulfilment",
#     fields=[
#         fulfilment_id,
#         activation_id,
#         activation_count,
#         overdraft_count,
#         start_date,
#         fulfilment_date_time,
#         license_file_definition_name,
#         license,
#         license_filename,
#         ### attributes
#         att_comment,
#         att_hcltech_email,
#         att_hcltech_representative,
#         att_order_number,
#         att_product_name,
#         att_product_version,
#         att_sales_contact_email])
#
# def process_bundle_work_book(schema) -> list[SchemaEntity]:
#     current = None
#     local_entities: list[SchemaEntity] = []
#
#     with closing(load_workbook(args.import_file, read_only=True)) as work_book:
#         work_sheet = work_book.active
#
#         headers = schema.validate_sheet(work_sheet)
#         ##DEBUG
#         print(f'columns \n\t{"\n\t".join(headers)}')
#
#         # Process data rows
#         for row_num, row in enumerate(
#                 work_sheet.iter_rows(min_row=2, values_only=True),
#                 start=2):
#
#             record = dict(zip(headers, row))
#             # print(record)
#             if not Schema.row_is_empty(record):
#                 ## not a blank row
#                 if current is None or (
#                         record[product_name.name] and record[product_name.name] != current.get_value(product_name)):
#
#                     current = schema.create_entity(record, row_num)
#
#                     local_entities.append(current)
#                 else:
#                     current.validate_matching(record, row_num)
#
#                 if record[skus.name]:
#                     current.append_value(skus, record[skus.name])
#
#                 if record[bundles.name]:
#                     current.append_value(bundles, record[bundles.name])
#             #end if not Schema.row_is_empty(record):
#         #end for row_num
#
#         return local_entities
#
# def process_fulfilment_work_book(schema) -> list[SchemaEntity]:
#     current = None
#     local_entities: list[SchemaEntity] = []
#
#     with closing(load_workbook(args.import_file, read_only=True)) as work_book:
#         work_sheet = work_book.active
#
#         headers = schema.validate_sheet(work_sheet)
#         ##DEBUG
#         print(f'columns \n\t{"\n\t".join(headers)}')
#
#         # Process data rows
#         for row_num, row in enumerate(
#                 work_sheet.iter_rows(min_row=2, values_only=True),
#                 start=2):
#
#             record = dict(zip(headers, row))
#             # print(record)
#             if not Schema.row_is_empty(record):
#                 ## not a blank row
#                 if current is None or (
#                         record[product_name.name] and record[product_name.name] != current.get_value(product_name)):
#
#                     current = schema.create_entity(record, row_num)
#
#                     local_entities.append(current)
#                 else:
#                     current.validate_matching(record, row_num)
#
#             #end if not Schema.row_is_empty(record):
#         #end for row_num
#
#         return local_entities


## generate XML
# fulfilments = process_fulfilment_work_book(fulfilment_schema)
#
# entities = process_bundle_work_book(bundle_schema)
#
# xml = XMLBuilder()
# xml.initialize("products")
#
# for ent in entities:
#     print(ent.get_value(product_name))
#
#     xml.push_tag("product")
#     xml.push_cdata("productName", ent.get_value(product_name))
#     xml.push_cdata("version", ent.get_value(product_version))
#     xml.push_cdata("state", ent.get_value(state))
#     xml.push_tags("features", "feature", "primaryKeys")
#     xml.push_cdata("name", ent.get_value(feature_name))
#     xml.push_cdata("version", ent.get_value(feature_version))
#     xml.pop_tag("primaryKeys")
#     xml.push_cdata("count", ent.get_value(feature_count))
#     xml.pop_tag("features")
#     xml.push_tags("categoryAttributes")
#
#     if ent.has_value(bundles):
#         xml.push_tags("categoryAttribute")
#         xml.push_cdata("attributeName", "BUNDLES")
#         xml.push_cdata("attributeValue", ";".join(ent.get_value(bundles)))
#         xml.pop_tag("categoryAttribute")
#
#     if ent.has_value(skus):
#         xml.push_tags("categoryAttribute")
#         xml.push_cdata("attributeName", "SKUS")
#         xml.push_cdata("attributeValue", ";".join(ent.get_value(skus)))
#         xml.pop_tag("categoryAttribute")
#
#     xml.pop_tag("product")
#
# xml.pop_tag("products")

bundles = bundle.Bundle()

bundles.process_work_book(args.import_file)

xml = bundles.process_entities()

with open(args.export_file, "w", encoding="utf-8") as f:
    f.write(xml.text())
