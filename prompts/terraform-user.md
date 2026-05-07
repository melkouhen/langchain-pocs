**Role:** Senior Cloud Engineer & Terraform Architect.

**Task:** Generate a production-ready Terraform project structure to deploy Google Cloud Storage (GCS) buckets.

**Technical Specifications:**
- **Resources:** GCS buckets (dev and prod environments)
  - Dev bucket: `my-bucket-elkouhen-dev`
  - Prod bucket: `my-bucket-elkouhen-prod`
- **Provider:** GCP, Region `europe-west9`
- **Project Root Path:** `/Users/melkouhen/audit-tools/test-langchain/work`
- **Environments:** `dev` and `prod` (separate state files and configurations)

**Important:**
1. **Search the knowledge base first** for "Google Cloud Storage terraform module" to find documented patterns and modules
2. **Use the terraform-google-modules/cloud-storage module** if available in the knowledge base (preferred over raw resources)
3. Follow the module's input variables, outputs, and best practices documentation
4. Apply all CRITICAL and MAJOR fixes from the review phase before final delivery
