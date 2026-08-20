
from openpyxl import load_workbook

class Bundle:
    product_name = "productName"
    product_version = "productVersion"
    state = "state"
    feature_name = "featureName"
    feature_version = "featureVersion"
    feature_count = "featureCount"
    skus = "skus"
    bundles = "bundles"

    required_fields = [
        product_name,
        product_version,
        state,
        feature_name,
        feature_version,
        feature_count
    ]

    expected_fields = {
        product_name,
        product_version,
        state,
        feature_name,
        feature_version,
        feature_count,
        skus,
        bundles
    }

    @staticmethod
    def validate_header(sheet):

        raw_headers = next(sheet.iter_rows(min_row=1, max_row=1, values_only=True))

        parsed_headers = []

        for col_num, header in enumerate(raw_headers, start=1):
            if header is None or str(header).strip() == "":
                raise ValueError(f"Unnamed header found in column {col_num}")

            parsed_headers.append(str(header).strip())

        # Check for duplicates
        duplicates = {h for h in parsed_headers if parsed_headers.count(h) > 1}
        if duplicates:
            raise ValueError(f"Duplicate headers found: {sorted(duplicates)}")

        # Check expected vs actual
        actual_fields = set(parsed_headers)

        missing = Bundle.expected_fields - actual_fields
        if missing:
            raise ValueError(f"Missing columns: {sorted(missing)}")

        extra = actual_fields - Bundle.expected_fields
        if extra:
            raise ValueError(f"Unexpected columns: {sorted(extra)}")

        return parsed_headers

    @staticmethod
    def has_value(value):
        return value is not None and str(value).strip() != ""

    @staticmethod
    def validate_fields(record, row_num):
        missing = [
            field
            for field in Bundle.required_fields
            if not Bundle.has_value(record.get(field))
        ]

        if missing:
            raise ValueError(f"Missing required field(s) at row {row_num}: {', '.join(missing)}")

    @staticmethod
    def validate_required_fields(record, row_num):
        missing = [
            field
            for field in Bundle.required_fields
            if not Bundle.has_value(record.get(field))
        ]

        if missing:
            raise ValueError(f"Missing required field(s) at row {row_num}: {', '.join(missing)}")

    def __init__(self, record):
        self.productName = record[Bundle.product_name]
        self.productVersion = record[Bundle.product_version]
        self.state = record[Bundle.skus]
        self.featureName = record[Bundle.feature_name]
        self.featureVersion = record[Bundle.feature_version]
        self.featureCount = record[Bundle.feature_count]
        self.skus: list[str] = []
        self.bundles: list[str] = []

    # def __init__(self,
    #              product_name:str,
    #              product_version:str,
    #              state:str,
    #              feature_name:str,
    #              feature_version:str,
    #              feature_count:str):
    #     self.productName = product_name
    #     self.productVersion = product_version
    #     self.state = state
    #     self.featureName = feature_name
    #     self.featureVersion = feature_version
    #     self.featureCount = feature_count
    #     self.skus: list[str] = []
    #     self.bundles: list[str] = []



    def validate_matching(self, record, row_num):
        for field in self.required_fields:
            value = record.get(field)

            # Blank value is allowed
            if not Bundle.has_value(value):
                continue

            current_value = getattr(self, field)

            if str(value) != str(current_value):
                raise ValueError(
                    f"Row {row_num}: {field} has value '{value}' "
                    f"but current bundle has '{current_value}'"
                )
