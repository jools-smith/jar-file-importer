import argparse
from openpyxl import load_workbook
from dataclasses import dataclass, field


def cdata(value):
    return f"<![CDATA[{value}]]>"

def has_value(value):
    return value is not None and str(value).strip() != ""


def validate_required_fields(record, required_fields, row_num):
    missing = [
        field
        for field in required_fields
        if not has_value(record.get(field))
    ]

    if missing:
        raise ValueError(f"Missing required field(s) at row {row_num}: {', '.join(missing)}")

@dataclass
class Bundle:
    productName:str
    productVersion:str
    state:str
    featureName:str
    featureCount:int
    skus: list[str] = field(default_factory=list)
    bundles: list[str] = field(default_factory=list)

parser = argparse.ArgumentParser(
    description="Process bundled product definitions spreadsheet"
)

parser.add_argument("-i", "--import", dest="import_file", required=True, help="import file")
parser.add_argument("-e", "--export", dest="export_file", required=True, help="export file")

args = parser.parse_args()


print(f"Using import file {args.import_file} export to {args.export_file}")

wb = load_workbook(args.import_file)
ws = wb.active

headers = [cell.value for cell in ws[1]]
print(headers)

required_fields = [
    "productName",
    "productVersion",
    "state",
    "featureName",
    "featureCount"
]

bundles = []

current = None
# Process data rows
for row_num, row in enumerate(
        ws.iter_rows(min_row=2, values_only=True),
        start=2):
    record = dict(zip(headers, row))

    if all(cell is None or str(cell).strip() == "" for cell in row):
        ## ignore blank rows
        continue

    if current is None or (record["productName"] and record["productName"] != current.productName):
        validate_required_fields(record, required_fields, row_num)

        current = Bundle(
            productName=record["productName"],
            productVersion = record["productVersion"],
            state=record["state"],
            featureName=record["featureName"],
            featureCount=record["featureCount"])
        bundles.append(current)

    if record["skus"]:
        current.skus.append(record["skus"])

    if record["bundles"]:
        current.bundles.append(record["bundles"])

## generate XML
with open(args.export_file, "w", encoding="utf-8") as f:
    f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
    f.write('\n') # space may be important
    f.write('<products xmlns="urn:com.macrovision:flexnet/operations/exportimport">\n')

    for bundle in bundles:
        f.write(f'<product>\n')
        f.write(f'<productName>{cdata(bundle.productName)}</productName>\n')
        f.write(f'<version>{cdata(bundle.productVersion)}</version>\n')
        f.write(f'<state>{bundle.state}</state>\n')
        f.write(f'<features>\n')
        f.write(f'<feature>\n')
        f.write(f'<primaryKeys>\n')
        f.write(f'<name>{cdata(bundle.featureName)}</name>\n')
        f.write(f'<version><![CDATA[0]]></version>\n')
        f.write(f'</primaryKeys>\n')
        f.write(f'<count>{bundle.featureCount}</count>\n')
        f.write(f'</feature>\n')
        f.write(f'</features>\n')
        f.write(f'<categoryAttributes>\n')
        f.write(f'<categoryAttribute>\n')
        f.write(f'<attributeName><![CDATA[BUNDLES]]></attributeName>\n')
        f.write(f'<attributeValue>{cdata(";".join(bundle.bundles))}</attributeValue>\n')
        f.write(f'</categoryAttribute>\n')
        f.write(f'<categoryAttribute>\n')
        f.write(f'<attributeName><![CDATA[SKUS]]></attributeName>\n')
        f.write(f'<attributeValue>{cdata(";".join(bundle.skus))}</attributeValue>\n')
        f.write(f'</categoryAttribute>\n')
        f.write(f'</categoryAttributes>\n')
        f.write(f'</product>\n')

    f.write('</products>\n')