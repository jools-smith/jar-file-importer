from abc import ABC
from dataclasses import dataclass
from typing import final

from schema import Schema, SchemaField, SchemaEntity, RecordWrapper
from xml_builder import XMLBuilder

@final
@dataclass(frozen=True)
class Bundle(Schema):
    product_name = SchemaField("productName")
    product_version = SchemaField("productVersion")
    state = SchemaField("state")
    feature_name = SchemaField("featureName")
    feature_version = SchemaField("featureVersion")
    feature_count = SchemaField("featureCount")
    skus = SchemaField("skus", False)
    skus_count = SchemaField("skuCount", False)
    bundles = SchemaField("bundles", False)
    bundles_count = SchemaField("bundleSkuCount", False)

    def __init__(self):
        super().__init__(
            name = "bundle",
            fields = [
                Bundle.product_name,
                Bundle.product_version,
                Bundle.state,
                Bundle.feature_name,
                Bundle.feature_version,
                Bundle.feature_count,
                Bundle.skus,
                Bundle.skus_count,
                Bundle.bundles,
                Bundle.bundles_count
            ]
        )

    def process_worksheet(self, work_sheet) -> Schema:
        current = None
        # local_entities: list[SchemaEntity] = []

        headers = self.validate_sheet(work_sheet)
        ##DEBUG
        print(f'columns \n\t{"\n\t".join(headers)}')

        # Process data rows
        for row_num, row in enumerate(
                work_sheet.iter_rows(min_row=2, values_only=True),
                start=2):

            row = RecordWrapper(dict(zip(headers, row)))

            # print(record)
            if not row.is_empty():
                ## not a blank row
                if current is None or (
                        row.has(Bundle.product_name) and row.get(Bundle.product_name) != current.get_value(Bundle.product_name)):

                    current = self.create_entity_with_required_fields(row.get_row(), row_num)

                    self.entities.append(current)
                else:
                    current.validate_matching(row.get_row(), row_num)


                if row.has(Bundle.skus):
                    self.assert_field_numeric(row.get_row(), row_num, Bundle.skus_count)

                    current.append_value(Bundle.skus,f"{row.get(Bundle.skus)}:{row.get(Bundle.skus_count)}")
                else:
                    if row.has(Bundle.skus_count):
                        raise ValueError(
                            f"at row {row_num} - {Bundle.skus_count.name}({row.get(Bundle.skus_count)}) should not be defined")

                if row.has(Bundle.bundles):
                    self.assert_field_numeric(row.get_row(), row_num, Bundle.skus_count)
                    current.append_value(Bundle.bundles, f"{row.get(Bundle.bundles)}:{row.get(Bundle.bundles_count)}")
                else:
                    if row.has(Bundle.bundles_count):
                        raise ValueError(
                            f"at row {row_num} - {Bundle.bundles_count.name}({row.get(Bundle.bundles_count)}) should not be defined")

            #end if not Schema.row_is_empty(record):
        #end for row_num
        return self

    def process_entities(self) -> XMLBuilder:
        xml = XMLBuilder()
        xml.initialize("products")

        for ent in self.entities:
            print(ent.get_value(Bundle.product_name))

            xml.push_tag("product")
            xml.push_cdata("productName", ent.get_value(Bundle.product_name))
            xml.push_cdata("version", ent.get_value(Bundle.product_version))
            xml.push_cdata("state", ent.get_value(Bundle.state))
            xml.push_tags("features", "feature", "primaryKeys")
            xml.push_cdata("name", ent.get_value(Bundle.feature_name))
            xml.push_cdata("version", ent.get_value(Bundle.feature_version))
            xml.pop_tag("primaryKeys")
            xml.push_cdata("count", ent.get_value(Bundle.feature_count))
            xml.pop_tag("features")
            xml.push_tags("categoryAttributes")

            if ent.has_value(Bundle.bundles):
                xml.push_tags("categoryAttribute")
                xml.push_cdata("attributeName", "BUNDLES")
                xml.push_cdata("attributeValue", ";".join(ent.get_value(Bundle.bundles)))
                xml.pop_tag("categoryAttribute")

            if ent.has_value(Bundle.skus):
                xml.push_tags("categoryAttribute")
                xml.push_cdata("attributeName", "SKUS")
                xml.push_cdata("attributeValue", ";".join(ent.get_value(Bundle.skus)))
                xml.pop_tag("categoryAttribute")

            xml.pop_tag("product")

        xml.pop_tag("products")

        return xml