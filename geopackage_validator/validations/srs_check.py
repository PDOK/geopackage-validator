from typing import Iterable, Tuple

from geopackage_validator.constants import ALLOWED_PROJECTIONS_LIST

from geopackage_validator.validations import validator


def srs_check_query(dataset) -> Iterable[Tuple[str, str]]:
    srs_list = dataset.ExecuteSQL(
        """
        SELECT organization, organization_coordsys_id AS id, srs_name 
        FROM gpkg_geometry_columns 
        JOIN gpkg_spatial_ref_sys gsrs on gsrs.srs_id = gpkg_geometry_columns.srs_id;"""
    )

    for organization, organization_coordsys_id, srs_name in srs_list:
        yield organization, organization_coordsys_id, srs_name

    dataset.ReleaseResultSet(srs_list)


def srs_equal_check_query(dataset) -> Iterable[str]:
    srs_list = dataset.ExecuteSQL("SELECT srs_id FROM gpkg_geometry_columns;")

    for (srs,) in srs_list:
        yield srs

    dataset.ReleaseResultSet(srs_list)


class SrsValidator(validator.Validator):
    """Only the following EPSG spatial reference systems are allowed: 28992, 3034, 3035, 3038, 3039, 3040, 3041, 3042, 3043, 3044, 3045, 3046, 3047, 3048, 3049, 3050, 3051, 4258, 4936, 4937, 5730, 7409."""

    code = 12
    level = validator.ValidationLevel.ERROR
    message = "Found in 'gpkg_spatial_ref_sys' {srs_organisation} {srs_id}. {srs_name} is not allowed."

    def check(self) -> Iterable[str]:
        srs_metadata = srs_check_query(self.dataset)
        return self.srs_check(srs_metadata)

    @classmethod
    def srs_check(cls, srs_list: Iterable[Tuple[str, str]]):
        assert srs_list is not None

        results = []

        for srs_organisation, srs_id, srs_name in srs_list:

            if srs_organisation != "EPSG":
                results.append(
                    cls.message.format(
                        srs_organisation=srs_organisation,
                        srs_id=srs_id,
                        srs_name=srs_name,
                    )
                )
                continue  # prevent duplicate error message for the same srs entry

            if srs_id not in ALLOWED_PROJECTIONS_LIST:
                results.append(
                    cls.message.format(
                        srs_organisation=srs_organisation,
                        srs_id=srs_id,
                        srs_name=srs_name,
                    )
                )

        return results


class SrsEqualValidator(validator.Validator):
    """It is required to give all GEOMETRY features the same default spatial reference system."""

    code = 13
    level = validator.ValidationLevel.ERROR
    message = "Found srs are: {srs}."

    def check(self) -> Iterable[str]:
        srs_list = srs_equal_check_query(self.dataset)
        return self.check_srs_equal(srs_list)

    def check_srs_equal(self, srs_list: Iterable[str]):
        assert srs_list is not None
        srs_set = set(srs_list)
        if len(srs_set) > 1:
            return [self.message.format(srs=", ".join([str(x) for x in srs_set]))]

        return []
