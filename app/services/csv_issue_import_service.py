"""CSV issue import service — parse and validate CSV files for session creation.

This module provides utilities to parse issue CSV files uploaded during session
creation. It validates required columns, normalizes header names, checks for
duplicate issue keys, and returns structured issue data for ingestion.
"""

from __future__ import annotations

import csv
from typing import Any, TextIO


class CSVValidationError(Exception):
    """Raised when CSV parsing or validation fails.

    :param message: Human-readable error detail.
    """

    def __init__(self, message: str) -> None:
        """Initialise with a validation error message."""
        super().__init__(message)


class CSVIssueImportService:
    """Service for parsing and validating CSV issue files."""

    # Required columns that must be present in the CSV header.
    REQUIRED_COLUMNS = ["issue type", "issue key", "summary"]

    # Optional columns that will be mapped if present.
    OPTIONAL_COLUMNS = ["description"]

    # Valid Issue Type values (case-insensitive).
    VALID_ISSUE_TYPES = ["story", "bug"]

    @staticmethod
    def _normalize_header(header: str) -> str:
        """Normalize a CSV header name to lowercase with stripped whitespace.

        :param header: Raw header string from CSV.
        :returns: Normalized header string.
        """
        return header.strip().lower()

    @staticmethod
    def _validate_headers(headers: list[str]) -> dict[str, int]:
        """Validate that required columns are present and map column indices.

        :param headers: List of normalized header names.
        :returns: Mapping from normalized column name to column index.
        :raises CSVValidationError: If required columns are missing.
        """
        header_map = {h: i for i, h in enumerate(headers)}
        missing = [
            col
            for col in CSVIssueImportService.REQUIRED_COLUMNS
            if col not in header_map
        ]
        if missing:
            # Convert back to title case for error message.
            missing_display = [col.title() for col in missing]
            raise CSVValidationError(
                f"Missing required CSV columns: {', '.join(missing_display)}"
            )
        return header_map

    @staticmethod
    def _validate_issue_type(issue_type: str, row_num: int) -> None:
        """Validate that Issue Type value is one of the allowed values.

        :param issue_type: Issue Type value from CSV row.
        :param row_num: Row number for error reporting (1-indexed data row).
        :raises CSVValidationError: If Issue Type is invalid.
        """
        if issue_type.strip().lower() not in CSVIssueImportService.VALID_ISSUE_TYPES:
            valid_types = ", ".join(
                [t.title() for t in CSVIssueImportService.VALID_ISSUE_TYPES]
            )
            raise CSVValidationError(
                f"Invalid Issue Type '{issue_type}' at row {row_num}. "
                f"Must be one of: {valid_types}"
            )

    @staticmethod
    def _validate_required_fields(row: dict[str, str], row_num: int) -> None:
        """Validate that required fields have non-empty values.

        :param row: Dictionary of field name to field value.
        :param row_num: Row number for error reporting (1-indexed data row).
        :raises CSVValidationError: If any required field is empty.
        """
        for field in ["issue_type", "issue_key", "summary"]:
            value = row.get(field, "").strip()
            if not value:
                field_display = field.replace("_", " ").title()
                raise CSVValidationError(
                    f"Empty {field_display} at row {row_num}. "
                    f"All required fields must have values."
                )

    @staticmethod
    def parse_issues_csv(csv_file: TextIO) -> list[dict[str, Any]]:
        """Parse a CSV file containing issues for a SCRUM poker session.

        Expected CSV format:
        - Header row with column names (case-insensitive, whitespace-trimmed).
        - Required columns: Issue Type, Issue Key, Summary.
        - Optional columns: Description.
        - Extra columns are ignored.

        Validation rules:
        - Issue Type must be "Story" or "Bug" (case-insensitive).
        - Issue Key values must be unique within the CSV.
        - All required fields must have non-empty values.
        - At least one data row must be present.

        :param csv_file: Text file object containing CSV data.
        :returns: List of issue dictionaries with normalized field names.
        :raises CSVValidationError: If validation fails.
        """
        
        reader = csv.reader(csv_file)

        # Read and normalize headers.
        try:
            raw_headers = next(reader)
        except StopIteration:
            raise CSVValidationError("CSV file is empty.")

        normalized_headers = [
            CSVIssueImportService._normalize_header(h) for h in raw_headers
        ]

        # Validate required columns are present.
        header_map = CSVIssueImportService._validate_headers(normalized_headers)

        # Parse data rows.
        issues: list[dict[str, Any]] = []
        seen_keys: set[str] = set()
        row_num = 1  # Data row counter (1-indexed).

        for raw_row in reader:
            row_num += 1

            # Build issue dict from required and optional columns.
            issue: dict[str, Any] = {}

            # Extract required fields.
            issue["issue_type"] = raw_row[header_map["issue type"]].strip()
            issue["issue_key"] = raw_row[header_map["issue key"]].strip()
            issue["summary"] = raw_row[header_map["summary"]].strip()

            # Extract optional fields.
            if "description" in header_map:
                issue["description"] = raw_row[header_map["description"]].strip()
            else:
                issue["description"] = None

            # Validate required fields are non-empty.
            CSVIssueImportService._validate_required_fields(issue, row_num)

            # Validate Issue Type value.
            CSVIssueImportService._validate_issue_type(issue["issue_type"], row_num)

            # Check for duplicate Issue Key.
            if issue["issue_key"] in seen_keys:
                raise CSVValidationError(
                    f"Duplicate Issue Key '{issue['issue_key']}' found at row {row_num}."
                )
            seen_keys.add(issue["issue_key"])

            issues.append(issue)

        # Validate at least one issue was provided.
        if not issues:
            raise CSVValidationError("CSV file contains no issues.")

        return issues
