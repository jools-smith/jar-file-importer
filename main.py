import argparse
from openpyxl import load_workbook

from Bundle import Bundle
from XMLBuilder import XMLBuilder

parser = argparse.ArgumentParser(
    description="Process bundled product definitions spreadsheet"
)

parser.add_argument("-i", "--import", dest="import_file", required=True, help="import file")
parser.add_argument("-e", "--export", dest="export_file", required=True, help="export file")

args = parser.parse_args()


print(f"Using import file {args.import_file}")
print(f"export to {args.export_file}")

wb = load_workbook(args.import_file)
ws = wb.active

headers = Bundle.validate_header(ws)
print(headers)

current = None
bundles = []

# Process data rows
for row_num, row in enumerate(
        ws.iter_rows(min_row=2, values_only=True),
        start=2):
    record = dict(zip(headers, row))

    if all(cell is None or str(cell).strip() == "" for cell in row):
        ## ignore blank rows
        continue

    if current is None or (record[Bundle.product_name] and record[Bundle.product_name] != current.productName):
        Bundle.validate_required_fields(record, row_num)

        current = Bundle(record)

        bundles.append(current)
    else:
        current.validate_matching(record, row_num)

    if record[Bundle.skus]:
        current.skus.append(record[Bundle.skus])

    if record[Bundle.bundles]:
        current.bundles.append(record[Bundle.bundles])

## generate XML

xml = XMLBuilder()
xml.initialize("products")

for bundle in bundles:
    xml.push_tag("product")
    xml.push_cdata("productName", bundle.productName)
    xml.push_cdata("productVersion", bundle.productVersion)
    xml.push_cdata("state", bundle.state)
    xml.push_tags("features", "feature", "primaryKeys")
    xml.push_cdata("name", bundle.featureName)
    xml.push_cdata("version", bundle.featureVersion)
    xml.pop_tag("primaryKeys")
    xml.push_cdata("count", bundle.featureCount)
    xml.pop_tag("features")

    xml.push_tags("categoryAttributes", "categoryAttribute")
    xml.push_cdata("attributeName", "BUNDLES")
    xml.push_cdata("attributeValue", ";".join(bundle.bundles))
    xml.pop_tag("categoryAttribute")
    xml.push_tags("categoryAttribute")
    xml.push_cdata("attributeName", "SKUS")
    xml.push_cdata("attributeValue", ";".join(bundle.skus))
    xml.pop_tag("product")

xml.pop_tag("products")

with open(args.export_file, "w", encoding="utf-8") as f:
    f.write(xml.text())