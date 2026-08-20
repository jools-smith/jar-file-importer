import argparse

from openpyxl import load_workbook

from XMLBuilder import XMLBuilder
from schema import SchemaField, SchemaEntity, Schema

parser = argparse.ArgumentParser(
    description="Process bundled product definitions spreadsheet"
)

parser.add_argument("-i", "--import", dest="import_file", required=True, help="import file")
parser.add_argument("-e", "--export", dest="export_file", required=True, help="export file")

args = parser.parse_args()


print(f"Using import file {args.import_file}")
print(f"export to {args.export_file}")

## column names
product_name = SchemaField("productName", True)
product_version = SchemaField("productVersion", True)
state = SchemaField("state", True)
feature_name = SchemaField("featureName", True)
feature_version = SchemaField("featureVersion", True)
feature_count = SchemaField("featureCount", True)
skus = SchemaField("skus", False)
bundles = SchemaField("bundles", False)

## schema definition
schema = Schema(
    name = "bundle",
    fields = [
        product_name,
        product_version,
        state,
        feature_name,
        feature_version,
        feature_count,
        skus,
        bundles])


work_sheet = load_workbook(args.import_file).active

headers = schema.validate_sheet(work_sheet)
print(headers)

current = None
entities: list[SchemaEntity] = []

# Process data rows
for row_num, row in enumerate(
        work_sheet.iter_rows(min_row=2, values_only=True),
        start=2):

    record = dict(zip(headers, row))
    # print(record)
    if Schema.row_is_empty(record):
        continue

    if (current is None) or (record[product_name.name] and record[product_name.name] != current.get_value(product_name)):

        current = schema.create_entity(record, row_num)

        entities.append(current)
    else:
        current.validate_matching(record, row_num)

    if record[skus.name]:
        current.append_value(skus, record[skus.name])

    if record[bundles.name]:
        current.append_value(bundles, record[bundles.name])

## generate XML

xml = XMLBuilder()
xml.initialize("products")

for ent in entities:
    xml.push_tag("product")
    xml.push_cdata("productName", ent.get_value(product_name))
    xml.push_cdata("productVersion", ent.get_value(product_version))
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