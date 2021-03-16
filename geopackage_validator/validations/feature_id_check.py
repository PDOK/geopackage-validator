from typing import Iterable, Tuple, List

from geopackage_validator.validations import validator

from geopackage_validator import utils


def query_feature_id(dataset) -> Iterable[Tuple[str, int]]:
    tables = utils.dataset_geometry_tables(dataset)

    for table, _, _ in tables:
        validations = dataset.ExecuteSQL(
            "SELECT '{table_name}' as table_name, count(*) as pk_present FROM pragma_table_info('{table_name}') where pk > 0".format(
                table_name=table
            )
        )
        for table_name, count in validations:
            yield table_name, count

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
