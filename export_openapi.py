"""
Script to export the FastAPI OpenAPI schema to a JSON file.

This script generates the OpenAPI specification from the FastAPI application
and saves it to a file. This is useful for:
- Documentation generation
- API client generation
- Sharing API specifications
- Version control of API schema
"""
import json
import yaml
from backend.main import app


def export_openapi_json(filename: str = "openapi.json"):
    """
    Export the OpenAPI schema as JSON.

    Args:
        filename: The output filename for the JSON schema
    """
    openapi_schema = app.openapi()
    with open(filename, "w") as f:
        json.dump(openapi_schema, f, indent=2)
    print(f"OpenAPI schema exported to {filename}")


def export_openapi_yaml(filename: str = "openapi.yaml"):
    """
    Export the OpenAPI schema as YAML.

    Args:
        filename: The output filename for the YAML schema
    """
    openapi_schema = app.openapi()
    with open(filename, "w") as f:
        yaml.dump(openapi_schema, f, sort_keys=False, default_flow_style=False)
    print(f"OpenAPI schema exported to {filename}")


def main():
    """Main entry point for the CLI script."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Export FastAPI OpenAPI schema to a file"
    )
    parser.add_argument(
        "--format",
        choices=["json", "yaml", "both"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--output",
        default="openapi",
        help="Output filename without extension (default: openapi)",
    )

    args = parser.parse_args()

    if args.format == "json":
        export_openapi_json(f"{args.output}.json")
    elif args.format == "yaml":
        export_openapi_yaml(f"{args.output}.yaml")
    elif args.format == "both":
        export_openapi_json(f"{args.output}.json")
        export_openapi_yaml(f"{args.output}.yaml")


if __name__ == "__main__":
    main()
