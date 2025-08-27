from typing import Iterable, Tuple, List

from geopackage_validator.validations import validator

from geopackage_validator import utils


def query_feature_id(dataset) -> Iterable[Tuple[str, int]]:
    tables = utils.dataset_geometry_tables(dataset)
    # validates that there is a primary key with integer/int, mediumint, smallint & tinyint
    query = """
                SELECT '{table_name}' AS table_name, count(*) AS pk_present FROM pragma_table_info('{table_name}') 
                    WHERE pk > 0 
                    AND type LIKE '%INT%' 
            """
    for table, _, _ in tables:
        validations = dataset.ExecuteSQL(query.format(table_name=table))
        for table_name, count in validations:
            yield table_name, count

        dataset.ReleaseResultSet(validations)


def query_sequence_for_autoincrement(dataset) -> Iterable[Tuple[str, int]]:
    tables = utils.dataset_geometry_tables(dataset)
    query = """
            SELECT '{table_name}' AS table_name, count(*) AS has_autoincrement
            FROM sqlite_sequence
            WHERE name = '{table_name}'
            """

    for table, _, _ in tables:
        validations = dataset.ExecuteSQL(query.format(table_name=table))
        for table_name, count in validations:
            yield table, count

        dataset.ReleaseResultSet(validations)


class FeatureIdValidator(validator.Validator):
    """Tables should have a feature id column with unique index."""

    code = 7
    level = validator.ValidationLevel.ERROR
    message = "Error found in table: {table_name}"

    def check(self) -> Iterable[str]:
        feature_ids = query_feature_id(self.dataset)
        return self.check_feature_id(feature_ids)

    @classmethod
    def check_feature_id(cls, feature_ids: Iterable[Tuple[str, int]]) -> List[str]:
        assert feature_ids is not None
        return [
            cls.message.format(table_name=table)
            for table, count in feature_ids
            if count != 1
        ]


class FeatureIdAutoincrementValidator(validator.Validator):
    """It is recommended for a feature id to have an autoincrement primary key."""

    code = 21
    level = validator.ValidationLevel.RECOMMENDATION
    message = "Found in table: {table_name}"

    def check(self) -> Iterable[str]:
        counts = query_sequence_for_autoincrement(self.dataset)
        return self.featureid_autoincrement_check(counts)

    @classmethod
    def featureid_autoincrement_check(
        cls, counts: Iterable[Tuple[str, int]]
    ) -> List[str]:
        assert counts is not None
        return [
            cls.message.format(table_name=table)
            for table, count in counts
            if count == 0
        ]
