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

                current = self.create_entity_with_all_fields(record, row_num)

                self.entities.append(current)

            #end if not Schema.row_is_empty(record):
        #end for row_num

    @staticmethod
    def process_attribute(xml, att_name, att_value):
        print(att_name, att_value)
        xml.push_tag("param")
        xml.push_cdata("name", att_name)
        if att_value:
            xml.push_cdata("value", att_value)
        else:
            xml.push_empty("value")
        xml.pop_tag("param")

    @staticmethod
    def process_attribute_name(xml, ent, attribute):
        xml.push_cdata(attribute.name, ent.get_value(attribute))

    def process_entities(self) -> XMLBuilder:
        xml = XMLBuilder()
        xml.initialize("importFulfillments")
        ##TODO needs completing
        for ent in self.entities:
            print(ent.get_value(self.fulfilment_id))

            xml.push_tag("fulfillmentRecord")
            self.process_attribute_name(xml, ent, self.fulfilment_id)
            xml.push_empty("migrationId")

            xml.push_tags("lifecycleInfo")
            xml.push_empty("fulfillAction")
            xml.pop_tag("lifecycleInfo")

            ## attributes
            for name in [
                self.att_comment,
                self.att_hcltech_email,
                self.att_hcltech_representative,
                self.att_order_number,
                self.att_product_name,
                self.att_product_version,
                self.att_sales_contact_email]:
                ## inject value
                self.process_attribute(xml, name.name, ent.get_value(name))

            self.process_attribute_name(xml, ent, self.start_date)
            xml.push_tags("licenseFiles", "licenseFile")
            self.process_attribute_name(xml, ent, self.license_file_definition_name)
            self.process_attribute_name(xml, ent, self.license)
            xml.pop_tag("licenseFiles")

            xml.push_tags("licenseFilenames", "licenseFilename")
            self.process_attribute_name(xml, ent, self.license_file_definition_name)
            self.process_attribute_name(xml, ent, self.license_filename)
            xml.pop_tag("licenseFilenames")

        xml.pop_tag("importFulfillments")

        return xml