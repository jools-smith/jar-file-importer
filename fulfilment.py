from abc import ABC
from dataclasses import dataclass

from schema import Schema, SchemaField, SchemaEntity
from xml_builder import XMLBuilder


@dataclass(frozen=True)
class Fulfilment(Schema):
    fulfilment_id = SchemaField("fulfillmentId")
    activation_id = SchemaField("activationId")
    activation_count = SchemaField("activationCount")
    overdraft_count = SchemaField("overdraftCount", False)
    start_date = SchemaField("startDate")

    att_comment = SchemaField("Comment", False)
    att_hcltech_email = SchemaField("HCLTech_Email", False)
    att_hcltech_representative = SchemaField("HCLTech_Representative", False)
    att_order_number = SchemaField("Order_Number", False)
    att_product_name = SchemaField("Product_Name", False)
    att_product_version = SchemaField("Product_Version", False)
    att_sales_contact_email = SchemaField("Sales_Contact_Email", False)
    fulfilment_date_time = SchemaField("fulfillDateTime")
    license_file_definition_name = SchemaField("licenseDefinitionName")
    license = SchemaField("license")
    license_filename = SchemaField("licfilename")


    def __init__(self):
        super().__init__(
            name = "fulfilment",
            fields = [
                self.fulfilment_id,
                self.activation_id,
                self.activation_count,
                self.overdraft_count,
                self.start_date,
                self.fulfilment_date_time,
                self.license_file_definition_name,
                self.license,
                self.license_filename,
                ### attributes
                self.att_comment,
                self.att_hcltech_email,
                self.att_hcltech_representative,
                self.att_order_number,
                self.att_product_name,
                self.att_product_version,
                self.att_sales_contact_email
            ]
        )

    def process_worksheet(self, work_sheet):

        headers = self.validate_sheet(work_sheet)
        ##DEBUG
        print(f'columns \n\t{"\n\t".join(headers)}')

        # Process data rows
        for row_num, row in enumerate(
                work_sheet.iter_rows(min_row=2, values_only=True),
                start=2):

            record = dict(zip(headers, row))

            if not Schema.row_is_empty(record):

                current = self.create_entity_with_required_fields(record, row_num)

                self.entities.append(current)

            #end if not Schema.row_is_empty(record):
        #end for row_num

    def process_entities(self):
        xml = XMLBuilder()
        xml.initialize("products")

        for ent in self.entities:
            print(ent.get_value(self.fulfilment_id))
            #
            # xml.push_tag("product")
            # xml.push_cdata("productName", ent.get_value(self.product_name))
            # xml.push_cdata("version", ent.get_value(self.product_version))
            # xml.push_cdata("state", ent.get_value(self.state))
            # xml.push_tags("features", "feature", "primaryKeys")
            # xml.push_cdata("name", ent.get_value(self.feature_name))
            # xml.push_cdata("version", ent.get_value(self.feature_version))
            # xml.pop_tag("primaryKeys")
            # xml.push_cdata("count", ent.get_value(self.feature_count))
            # xml.pop_tag("features")
            # xml.push_tags("categoryAttributes")
            #
            # if ent.has_value(self.bundles):
            #     xml.push_tags("categoryAttribute")
            #     xml.push_cdata("attributeName", "BUNDLES")
            #     xml.push_cdata("attributeValue", ";".join(ent.get_value(self.bundles)))
            #     xml.pop_tag("categoryAttribute")
            #
            # if ent.has_value(self.skus):
            #     xml.push_tags("categoryAttribute")
            #     xml.push_cdata("attributeName", "SKUS")
            #     xml.push_cdata("attributeValue", ";".join(ent.get_value(self.skus)))
            #     xml.pop_tag("categoryAttribute")
            #
            # xml.pop_tag("product")

        # xml.pop_tag("products")