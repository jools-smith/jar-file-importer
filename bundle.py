from abc import ABC
from dataclasses import dataclass

from schema import Schema, SchemaField, SchemaEntity
from xml_builder import XMLBuilder


@dataclass(frozen=True)
class Bundle(Schema):
    product_name = SchemaField("productName")
    product_version = SchemaField("productVersion")
    state = SchemaField("state")
    feature_name = SchemaField("featureName")
    feature_version = SchemaField("featureVersion")
    feature_count = SchemaField("featureCount")
    skus = SchemaField("skus", False)
    bundles = SchemaField("bundles", False)

    def __init__(self):
        super().__init__(
            name = "bundle",
            fields = [
                self.product_name,
                self.product_version,
                self.state,
                self.feature_name,
                self.feature_version,
                self.feature_count,
                self.skus,
                self.bundles
            ]
        )

    def process_worksheet(self, work_sheet):
        current = None
        # local_entities: list[SchemaEntity] = []

        headers = self.validate_sheet(work_sheet)
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
                        record[self.product_name.name] and record[self.product_name.name] != current.get_value(self.product_name)):

                    current = self.create_entity_with_required_fields(record, row_num)

                    self.entities.append(current)
                else:
                    current.validate_matching(record, row_num)

                if record[self.skus.name]:
                    current.append_value(self.skus, record[self.skus.name])

                if record[self.bundles.name]:
                    current.append_value(self.bundles, record[self.bundles.name])
            #end if not Schema.row_is_empty(record):
        #end for row_num

    def process_entities(self) -> XMLBuilder:
        xml = XMLBuilder()
        xml.initialize("products")

        for ent in self.entities:
            print(ent.get_value(self.product_name))

            xml.push_tag("product")
            xml.push_cdata("productName", ent.get_value(self.product_name))
            xml.push_cdata("version", ent.get_value(self.product_version))
            xml.push_cdata("state", ent.get_value(self.state))
            xml.push_tags("features", "feature", "primaryKeys")
            xml.push_cdata("name", ent.get_value(self.feature_name))
            xml.push_cdata("version", ent.get_value(self.feature_version))
            xml.pop_tag("primaryKeys")
            xml.push_cdata("count", ent.get_value(self.feature_count))
            xml.pop_tag("features")
            xml.push_tags("categoryAttributes")

            if ent.has_value(self.bundles):
                xml.push_tags("categoryAttribute")
                xml.push_cdata("attributeName", "BUNDLES")
                xml.push_cdata("attributeValue", ";".join(ent.get_value(self.bundles)))
                xml.pop_tag("categoryAttribute")

            if ent.has_value(self.skus):
                xml.push_tags("categoryAttribute")
                xml.push_cdata("attributeName", "SKUS")
                xml.push_cdata("attributeValue", ";".join(ent.get_value(self.skus)))
                xml.pop_tag("categoryAttribute")

            xml.pop_tag("product")

        xml.pop_tag("products")

        return xml