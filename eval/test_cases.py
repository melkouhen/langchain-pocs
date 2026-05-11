from dataclasses import dataclass


@dataclass(frozen=True)
class TestCase:
    id: str
    name: str
    prompt: str


TEST_CASES: list[TestCase] = [
    TestCase(
        id="tc01",
        name="Simple GCS Bucket",
        prompt=(
            "Create a simple Google Cloud Storage bucket for storing application logs "
            "in the dev environment. Follow security best practices."
        ),
    ),
    TestCase(
        id="tc02",
        name="Versioned ML Dataset Bucket",
        prompt=(
            "Create a Google Cloud Storage bucket for ML training datasets with "
            "versioning enabled and a lifecycle rule to delete versions older than 90 days. "
            "Enable UBLA (Uniform Bucket-Level Access)."
        ),
    ),
    TestCase(
        id="tc03",
        name="Multi-env Secure Bucket",
        prompt=(
            "Create a reusable Terraform module for a Google Cloud Storage bucket and deploy it "
            "in both dev and prod environments. Requirements: UBLA enabled, public access prevention "
            "on prod, optional versioning via variable, configurable storage class."
        ),
    ),
]
