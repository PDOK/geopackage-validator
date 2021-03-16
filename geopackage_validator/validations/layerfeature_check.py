from typing import Iterable, Tuple

from geopackage_validator.validations import validator


def query_tablefeature_counts(dataset) -> Iterable[Tuple[str, int, int]]:
    for table in dataset:
        table_name = table.GetName()

        table_featurecount = dataset.ExecuteSQL(
            "SELECT count(*) from {table_name}".format(table_name=table_name)
        )
        (table_count,) = table_featurecount.GetNextFeature()

        dataset.ReleaseResultSet(table_featurecount)

        yield table_name, table_count, table.GetFeatureCount()


class NonEmptyTableValidator(validator.Validator):
    """Tables must have at least one feature."""

    code = 2
    level = validator.ValidationLevel.ERROR
    message = "Error table: {table}"

    def check(self) -> Iterable[str]:
        counts = query_tablefeature_counts(self.dataset)
        return self.check_contains_features(counts)

    @classmethod
    def check_contains_features(cls, counts: Iterable[Tuple[str, int, int]]):
        assert counts is not None
        return [
            cls.message.format(table=table) for table, count, _ in counts if count == 0
        ]


class OGRIndexValidator(validator.Validator):
    """OGR indexed feature counts must be up to date"""

    code = 11
    level = validator.ValidationLevel.ERROR
    message = "OGR index for feature count is not up to date for table: {table}. Indexed feature count: {ogr_count}, real feature count: {count}"

    def check(self) -> Iterable[str]:
        counts = query_tablefeature_counts(self.dataset)
        return self.tablefeature_check_ogr_index(counts)

    @classmethod
    def tablefeature_check_ogr_index(cls, tables: Iterable[Tuple[str, int, int]]):
        assert tables is not None

        return [
            cls.message.format(table=name, count=count, ogr_count=ogr_count)
            for name, count, ogr_count in tables
            if count != ogr_count
        ]
