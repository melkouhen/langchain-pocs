# Cloud Run Ingress Security

<rule id="CLOUDRUN-INGRESS-SECURITY" severity="CRITICAL" scope="cloudrun" category="Security">
<title>Restrict Ingress to Minimum Required Access</title>

<description>
Cloud Run services should restrict ingress settings to the minimum required access level.
Using "all" ingress makes the service publicly accessible to the internet, which is
appropriate only for truly public services. Internal services should use "internal" or
"internal-and-cloud-load-balancing" to prevent unauthorized external access.
</description>

<problem>
Default or overly permissive ingress settings cause:
- Public exposure of internal services
- Unauthorized access to sensitive endpoints
- Bypass of authentication/authorization layers
- Attack surface expansion
- Compliance violations (GDPR, HIPAA, SOC2)
</problem>

<pattern id="correct">
<title>✅ Restrictive Ingress Configuration</title>

```hcl
# For internal services (backend APIs, admin panels)
resource "google_cloud_run_service" "internal_api" {
  name     = "internal-api"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/project/internal-api:latest"
      }
    }
  }

  metadata {
    annotations = {
      "run.googleapis.com/ingress" = "internal"  # ✓ Only accessible from VPC
    }
  }
}

# For services behind load balancer
resource "google_cloud_run_service" "backend" {
  name     = "backend-service"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/project/backend:latest"
      }
    }
  }

  metadata {
    annotations = {
      "run.googleapis.com/ingress" = "internal-and-cloud-load-balancing"  # ✓ LB only
    }
  }
}

# For truly public services only
resource "google_cloud_run_service" "public_website" {
  name     = "public-website"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/project/website:latest"
      }
    }
  }

  metadata {
    annotations = {
      "run.googleapis.com/ingress" = "all"  # ✓ Justified: public website
    }
  }
}
```

**Ingress Options:**
- `"internal"` — Only accessible from VPC networks (most restrictive)
- `"internal-and-cloud-load-balancing"` — VPC + Cloud Load Balancer
- `"all"` — Public internet access (least restrictive)
</pattern>

<antipattern id="incorrect">
<title>❌ Overly Permissive Ingress</title>

```hcl
# ❌ WRONG: Internal API exposed to internet
resource "google_cloud_run_service" "admin_panel" {
  name     = "admin-panel"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/project/admin:latest"
      }
    }
  }

  metadata {
    annotations = {
      "run.googleapis.com/ingress" = "all"  # ❌ Admin panel publicly accessible!
    }
  }
}

# ❌ WRONG: Database API with default (permissive) ingress
resource "google_cloud_run_service" "database_api" {
  name     = "database-api"
  location = var.region

  template {
    spec {
      containers {
        image = "gcr.io/project/db-api:latest"
      }
    }
  }
  # ❌ No ingress annotation = default may be "all"
}
```

**Consequences:**
❌ Sensitive services exposed to internet  
❌ Attackers can discover and exploit internal APIs  
❌ No network-level protection  
❌ Audit logs show unauthorized access attempts  
</antipattern>

<why>
**Security Principle:** Defense in depth — network isolation is the first layer

**Why restrictive ingress matters:**
1. **Network Segmentation**: Internal services shouldn't be reachable from internet
2. **Attack Surface Reduction**: Limits exposure to malicious actors
3. **Compliance**: Many frameworks require network isolation (PCI-DSS, HIPAA)
4. **Cost**: Public endpoints consume more egress bandwidth

**Common scenarios:**
- **Internal APIs**: Use `"internal"` (only VPC)
- **Services behind LB**: Use `"internal-and-cloud-load-balancing"`
- **Public websites**: Use `"all"` (document justification)
</why>

<when-to-apply>
**Use restrictive ingress for:**
- Admin panels and management interfaces
- Backend APIs consumed by other internal services
- Database access layers
- Internal tools and dashboards
- Services handling sensitive data

**Use "all" ingress only for:**
- Public-facing websites
- Public APIs with authentication
- Webhooks from external services
- Content delivery endpoints

**Document justification** when using "all" ingress
</when-to-apply>

<implementation-checklist>
- [ ] Audit all Cloud Run services for ingress settings
- [ ] Classify services: public vs internal
- [ ] Set `"internal"` for all internal services
- [ ] Use `"internal-and-cloud-load-balancing"` for services behind LB
- [ ] Justify and document any `"all"` ingress usage
- [ ] Test access from VPC (should work) and internet (should fail for internal)
- [ ] Update service IAM to require authentication even with restrictive ingress
- [ ] Configure VPC Connector for internal services accessing VPC resources
- [ ] Monitor Cloud Run audit logs for unauthorized access attempts
</implementation-checklist>

<related-rules>
- CLOUDRUN-IAM-INVOKER: Control who can invoke services
- CLOUDRUN-VPC-CONNECTOR: VPC connectivity for internal services
- TF-NO-SECRETS: Don't hardcode credentials
</related-rules>

<references>
- https://cloud.google.com/run/docs/securing/ingress
- https://cloud.google.com/run/docs/authenticating/overview
- https://cloud.google.com/run/docs/configuring/vpc-connectors
</references>

</rule>
