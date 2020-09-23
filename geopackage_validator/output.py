import json
from datetime import datetime
from typing import Dict, List

import pkg_resources  # part of setuptools


def log_output(
    errors: List[Dict[str, Dict[str, List[str]]]],
    filename: str = "",
    validations: Dict[str, str] = None,
    start_time: datetime = datetime.now(),
    duration_seconds: float = 0,
) -> None:
    if validations is None:
        validations = []
    script_version = pkg_resources.require("geopackage_validator")[0].version
    print(
        json.dumps(
            {
                "geopackage_validator_version": script_version,
                "start_time": start_time.strftime("%Y-%m-%dT%H:%M:%S.%f"),
                "duration_seconds": round(duration_seconds),
                "validated_geopackage": filename,
                "success": is_success(errors),
                "validations": validations,
                "errors": errors,
            },
            indent=4,
        )
    )


def is_success(result_list):

    for result in result_list:
        for key in result:
            if key.startswith("RQ"):
                return False

    return True
