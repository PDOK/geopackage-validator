import json


def log_output(errors):
    print(
        json.dumps(
            {"success": len(errors) == 0, "errors": errors}, indent=4, sort_keys=True
        )
    )
