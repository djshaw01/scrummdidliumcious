"""Unit tests for CSV issue import service — parsing, validation, and error handling.

Requirement trace:
- CSV parser accepts standard CSV format with header row.
- Required columns (Issue Type, Issue Key, Summary) are validated.
- Extra/unknown columns are ignored without error.
- Missing required columns raise ValidationError.
- Empty required field values raise ValidationError.
- Column names are case-insensitive and whitespace-normalized.
- Issue Type values must be "Story" or "Bug" (case-insensitive).
- Duplicate Issue Key values within a CSV are rejected.
"""

from __future__ import annotations

import io

import pytest

from app.services.csv_issue_import_service import (
    CSVIssueImportService,
    CSVValidationError,
)

# ── Valid CSV parsing ──────────────────────────────────────────────────────────


class TestValidCSVParsing:
    """Tests for successful CSV parsing with required columns."""

    def test_parse_minimal_required_columns(self):
        """CSV with only required columns is parsed successfully."""
        csv_content = (
            "Issue Type,Issue Key,Summary\n"
            "Story,PROJ-123,First issue\n"
            "Bug,PROJ-124,Second issue\n"
        )
        csv_file = io.StringIO(csv_content)

        issues = CSVIssueImportService.parse_issues_csv(csv_file)

        assert len(issues) == 2
        assert issues[0]["issue_type"] == "Story"
        assert issues[0]["issue_key"] == "PROJ-123"
        assert issues[0]["summary"] == "First issue"
        assert issues[0].get("description") is None

        assert issues[1]["issue_type"] == "Bug"
        assert issues[1]["issue_key"] == "PROJ-124"
        assert issues[1]["summary"] == "Second issue"

    def test_parse_with_optional_description_column(self):
        """CSV with optional Description column includes description values."""
        csv_content = (
            "Issue Type,Issue Key,Summary,Description\n"
            "Story,PROJ-123,First issue,First description\n"
            "Bug,PROJ-124,Second issue,\n"
        )
        csv_file = io.StringIO(csv_content)

        issues = CSVIssueImportService.parse_issues_csv(csv_file)

        assert len(issues) == 2
        assert issues[0]["description"] == "First description"
        assert issues[1]["description"] == ""

    def test_parse_with_extra_columns_ignores_them(self):
        """CSV with extra unknown columns ignores them without error."""
        csv_content = (
            "Issue Type,Issue Key,Summary,Priority,Assignee,Labels\n"
            "Story,PROJ-123,First issue,High,Alice,backend,api\n"
        )
        csv_file = io.StringIO(csv_content)

        issues = CSVIssueImportService.parse_issues_csv(csv_file)

        assert len(issues) == 1
        assert issues[0]["issue_key"] == "PROJ-123"
        # Extra columns are ignored.
        assert "priority" not in issues[0]
        assert "assignee" not in issues[0]

    def test_parse_with_case_insensitive_headers(self):
        """CSV with different-case headers is normalized correctly."""
        csv_content = "issue type,ISSUE KEY,Summary\n" "story,PROJ-123,First issue\n"
        csv_file = io.StringIO(csv_content)

        issues = CSVIssueImportService.parse_issues_csv(csv_file)

        assert len(issues) == 1
        assert issues[0]["issue_type"] == "story"
        assert issues[0]["issue_key"] == "PROJ-123"

    def test_parse_with_whitespace_in_headers(self):
        """CSV with extra whitespace in headers is normalized correctly."""
        csv_content = (
            " Issue Type , Issue Key , Summary \n" "Story,PROJ-123,First issue\n"
        )
        csv_file = io.StringIO(csv_content)

        issues = CSVIssueImportService.parse_issues_csv(csv_file)

        assert len(issues) == 1
        assert issues[0]["issue_type"] == "Story"

    def test_parse_with_quoted_fields(self):
        """CSV with quoted fields containing commas is parsed correctly."""
        csv_content = (
            "Issue Type,Issue Key,Summary,Description\n"
            'Story,PROJ-123,"Issue with, comma","Description with, comma"\n'
        )
        csv_file = io.StringIO(csv_content)

        issues = CSVIssueImportService.parse_issues_csv(csv_file)

        assert len(issues) == 1
        assert issues[0]["summary"] == "Issue with, comma"
        assert issues[0]["description"] == "Description with, comma"


# ── Required column validation ─────────────────────────────────────────────────


class TestRequiredColumnValidation:
    """Tests for missing required columns."""

    def test_missing_issue_type_column_raises_error(self):
        """CSV without Issue Type column raises CSVValidationError."""
        csv_content = "Issue Key,Summary\n" "PROJ-123,First issue\n"
        csv_file = io.StringIO(csv_content)

        with pytest.raises(CSVValidationError) as excinfo:
            CSVIssueImportService.parse_issues_csv(csv_file)

        assert "Issue Type" in str(excinfo.value)

    def test_missing_issue_key_column_raises_error(self):
        """CSV without Issue Key column raises CSVValidationError."""
        csv_content = "Issue Type,Summary\n" "Story,First issue\n"
        csv_file = io.StringIO(csv_content)

        with pytest.raises(CSVValidationError) as excinfo:
            CSVIssueImportService.parse_issues_csv(csv_file)

        assert "Issue Key" in str(excinfo.value)

    def test_missing_summary_column_raises_error(self):
        """CSV without Summary column raises CSVValidationError."""
        csv_content = "Issue Type,Issue Key\n" "Story,PROJ-123\n"
        csv_file = io.StringIO(csv_content)

        with pytest.raises(CSVValidationError) as excinfo:
            CSVIssueImportService.parse_issues_csv(csv_file)

        assert "Summary" in str(excinfo.value)

    def test_missing_multiple_required_columns_lists_all(self):
        """CSV missing multiple required columns lists all missing columns."""
        csv_content = "Summary\n" "First issue\n"
        csv_file = io.StringIO(csv_content)

        with pytest.raises(CSVValidationError) as excinfo:
            CSVIssueImportService.parse_issues_csv(csv_file)

        error_msg = str(excinfo.value)
        assert "Issue Type" in error_msg
        assert "Issue Key" in error_msg


# ── Required field value validation ────────────────────────────────────────────


class TestRequiredFieldValueValidation:
    """Tests for empty or missing required field values."""

    def test_empty_issue_type_raises_error(self):
        """Row with empty Issue Type raises CSVValidationError."""
        csv_content = "Issue Type,Issue Key,Summary\n" ",PROJ-123,First issue\n"
        csv_file = io.StringIO(csv_content)

        with pytest.raises(CSVValidationError) as excinfo:
            CSVIssueImportService.parse_issues_csv(csv_file)

        assert "Issue Type" in str(excinfo.value)
        assert "row 2" in str(excinfo.value).lower()

    def test_empty_issue_key_raises_error(self):
        """Row with empty Issue Key raises CSVValidationError."""
        csv_content = "Issue Type,Issue Key,Summary\n" "Story,,First issue\n"
        csv_file = io.StringIO(csv_content)

        with pytest.raises(CSVValidationError) as excinfo:
            CSVIssueImportService.parse_issues_csv(csv_file)

        assert "Issue Key" in str(excinfo.value)

    def test_empty_summary_raises_error(self):
        """Row with empty Summary raises CSVValidationError."""
        csv_content = "Issue Type,Issue Key,Summary\n" "Story,PROJ-123,\n"
        csv_file = io.StringIO(csv_content)

        with pytest.raises(CSVValidationError) as excinfo:
            CSVIssueImportService.parse_issues_csv(csv_file)

        assert "Summary" in str(excinfo.value)


# ── Issue Type validation ──────────────────────────────────────────────────────


class TestIssueTypeValidation:
    """Tests for valid Issue Type values."""

    def test_valid_story_issue_type(self):
        """Issue Type 'Story' is accepted."""
        csv_content = "Issue Type,Issue Key,Summary\n" "Story,PROJ-123,First issue\n"
        csv_file = io.StringIO(csv_content)

        issues = CSVIssueImportService.parse_issues_csv(csv_file)
        assert len(issues) == 1
        assert issues[0]["issue_type"] == "Story"

    def test_valid_bug_issue_type(self):
        """Issue Type 'Bug' is accepted."""
        csv_content = "Issue Type,Issue Key,Summary\n" "Bug,PROJ-123,First issue\n"
        csv_file = io.StringIO(csv_content)

        issues = CSVIssueImportService.parse_issues_csv(csv_file)
        assert len(issues) == 1
        assert issues[0]["issue_type"] == "Bug"

    def test_invalid_issue_type_raises_error(self):
        """Invalid Issue Type value raises CSVValidationError."""
        csv_content = "Issue Type,Issue Key,Summary\n" "Task,PROJ-123,First issue\n"
        csv_file = io.StringIO(csv_content)

        with pytest.raises(CSVValidationError) as excinfo:
            CSVIssueImportService.parse_issues_csv(csv_file)

        assert "Issue Type" in str(excinfo.value)
        assert "Story" in str(excinfo.value) or "Bug" in str(excinfo.value)


# ── Duplicate Issue Key validation ─────────────────────────────────────────────


class TestDuplicateIssueKeyValidation:
    """Tests for duplicate Issue Key detection."""

    def test_duplicate_issue_keys_raise_error(self):
        """CSV with duplicate Issue Key values raises CSVValidationError."""
        csv_content = (
            "Issue Type,Issue Key,Summary\n"
            "Story,PROJ-123,First issue\n"
            "Bug,PROJ-123,Duplicate key\n"
        )
        csv_file = io.StringIO(csv_content)

        with pytest.raises(CSVValidationError) as excinfo:
            CSVIssueImportService.parse_issues_csv(csv_file)

        assert "duplicate" in str(excinfo.value).lower()
        assert "PROJ-123" in str(excinfo.value)

    def test_unique_issue_keys_pass_validation(self):
        """CSV with all unique Issue Key values is accepted."""
        csv_content = (
            "Issue Type,Issue Key,Summary\n"
            "Story,PROJ-123,First issue\n"
            "Story,PROJ-124,Second issue\n"
            "Bug,PROJ-125,Third issue\n"
        )
        csv_file = io.StringIO(csv_content)

        issues = CSVIssueImportService.parse_issues_csv(csv_file)
        assert len(issues) == 3


# ── Empty CSV handling ─────────────────────────────────────────────────────────


class TestEmptyCSVHandling:
    """Tests for empty CSV files."""

    def test_empty_csv_raises_error(self):
        """CSV with no data rows raises CSVValidationError."""
        csv_content = ""
        csv_file = io.StringIO(csv_content)

        with pytest.raises(CSVValidationError) as excinfo:
            CSVIssueImportService.parse_issues_csv(csv_file)

        assert "empty" in str(excinfo.value).lower()

    def test_csv_with_only_headers_raises_error(self):
        """CSV with headers but no data rows raises CSVValidationError."""
        csv_content = "Issue Type,Issue Key,Summary\n"
        csv_file = io.StringIO(csv_content)

        with pytest.raises(CSVValidationError) as excinfo:
            CSVIssueImportService.parse_issues_csv(csv_file)

        assert (
            "no issues" in str(excinfo.value).lower()
            or "empty" in str(excinfo.value).lower()
        )
