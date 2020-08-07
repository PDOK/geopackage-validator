import json
from datetime import datetime
import pkg_resources  # part of setuptools


def log_output(
    errors, filename="", validations=[], start_time=datetime.now(), duration_seconds=0
):
    script_version = pkg_resources.require("geopackage_validator")[0].version
    print(
        json.dumps(
            {
                "geopackage_validator_version": script_version,
                "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "duration_seconds": round(duration_seconds),
                "validated_geopackage": filename,
                "success": len(errors) == 0,
                "validations": validations,
                "errors": errors,
            },
            indent=4,
        )
    )
