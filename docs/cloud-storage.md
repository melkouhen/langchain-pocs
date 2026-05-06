---
title: "Structuring Terraform Projects Like a Pro: Modules, Workspaces & Best Practices | by Bouachirhamza | Medium"
description: "Structuring Terraform Projects Like a Pro: Modules, Workspaces & Best Practices “Terraform works fine — until it doesn’t. Then you realize structure is everything.” If you’ve been using …"
url: https://medium.com/@bouachirhamza/structuring-terraform-projects-like-a-pro-modules-workspaces-best-practices-92c3f47df02b
site: Medium
author: Bouachirhamza
publish_date: 2025-07-16T10:14:54.667Z
---

[Sitemap](/sitemap/sitemap.xml)

# Structuring Terraform Projects Like a Pro: Modules, Workspaces & Best Practices

[![Bouachirhamza](https://miro.medium.com/v2/resize:fill:64:64/1*yDPs6Tll8wfuDLUolF-h7g.jpeg)](/@bouachirhamza?source=post_page---byline--92c3f47df02b---------------------------------------)

[Bouachirhamza](/@bouachirhamza?source=post_page---byline--92c3f47df02b---------------------------------------)

7 min readJul 16, 2025



\--

3



[Listen](/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D92c3f47df02b\&operation=register\&redirect=https%3A%2F%2Fmedium.com%2F%40bouachirhamza%2Fstructuring-terraform-projects-like-a-pro-modules-workspaces-best-practices-92c3f47df02b\&source=---header_actions--92c3f47df02b---------------------post_audio_button------------------)

Share

“Terraform works fine — until it doesn’t. Then you realize structure is everything.”

Press enter or click to view image in full size

!

If you’ve been using Terraform for a while, you’ve probably faced this situation: a `main.tf` file with 2000+ lines, no clear separation between staging and production, and a creeping feeling that any change might break something in another region.

I’ve been there too.

In this article, I’ll walk you through how to properly structure your Terraform code to make it clean, reusable, and scalable — without pulling your hair out. We’ll cover how to use **modules** effectively, when to rely on **workspaces** (and when not to), and a few battle-tested **best practices**.

Whether you’re managing three environments or thirty, this will help you sleep better at night.

## 🗂️ Project Structure Overview

One of the biggest steps toward sanity in Terraform is separating your code clearly — by **environment** and by **function**.

Here’s a typical structure I recommend:

```
terraform-project/
│
├── modules/               # Reusable building blocks
│   ├── vpc/
│   ├── ec2/
│   └── rds/
│
├── envs/                  # Separate configurations per environment
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── backend.tf
│   ├── staging/
│   └── prod/
│
├── global/                # Shared resources (e.g., IAM roles)
│   └── iam/
│       ├── main.tf
│       └── outputs.tf
│
└── README.md
```

## 🔍 Why this works:

* `modules/`: Contains reusable, *parameterized* code. Keeps logic DRY.
* `envs/`: Keeps production, staging, and development completely separate—different state files, backends, even providers if needed.
* `global/`: Holds resources that exist outside the environment lifecycle (e.g., shared S3 buckets, IAM roles).

## 🧭 Diagram: Terraform Project Layout

Here is a visual representation of the structure above:

I’ll now generate the diagram for this project layout. One moment…

!

✅ Great! Now we’ll hit the next section on **Modules**.

## 🔧 Understanding Modules

If you’ve written Terraform code before — even in a single file — you’ve already used a module. A module is just a folder with `.tf` files that define infrastructure.

But once your infrastructure grows, **custom modules** become essential.

## 🤔 Why use modules?

* **Reusability**: Define a VPC once, use it across environments.
* **Readability**: Your main files stay short and clear.
* **Maintainability**: Fix a bug in one place, update everywhere.

## 🧱 Example: A Simple `vpc` Module

Here’s a basic custom module layout:

```
modules/
└── vpc/
    ├── main.tf
    ├── variables.tf
    └── outputs.tf
```

`main.tf`

```
resource "aws_vpc" "main" {
  cidr_block = var.cidr_block
  tags = {
    Name = var.name
  }
}
```

`variables.tf`

```
variable "cidr_block" {}
variable "name" {}
```

`outputs.tf`

```
output "vpc_id" {
  value = aws_vpc.main.id
}
```

And from your environment code (`envs/dev/main.tf`):

```
module "vpc" {
  source     = "../../modules/vpc"
  cidr_block = "10.0.0.0/16"
  name       = "dev-vpc"
}
```

## 🚫 When not to use modules

* If the code is used **only once**, avoid creating a module just for the sake of it.
* Don’t over-nest: Keep modules shallow and focused (1 resource group per module is a good rule of thumb).

## 🧪 Workspaces: Environments the Right Way?

> *“Terraform workspaces are like duct tape — handy in a pinch, but maybe not how you want to build the whole plane.”*

Workspaces let you use the **same code** for multiple environments by switching the “workspace context.” In other words, Terraform separates your state file based on the active workspace (`default`, `dev`, `prod`, etc.).

Sounds great, right?

Well… *kind of.*

## 🧠 How Workspaces Work

Run these commands:

```
terraform workspace list
terraform workspace new staging
terraform workspace select prod
```

Terraform stores different `terraform.tfstate` files **within the same folder**, based on the selected workspace.

## ✅ Pros of Workspaces

* 🚀 Quick to set up
* ✅ Keeps state separate
* 🧪 Great for experimenting locally (e.g., `test`, `dev`, `playground`)

## 🚫 Cons (aka Terraform Horror Stories)

* **One folder to rule them all**: All your environments share the same code directory — mistakes happen fast.
* **No backend separation**: All workspaces write to the same backend, which is risky if you mess up state-locking.
* **Poor visibility**: It’s harder to tell what’s deployed where, especially in CI/CD pipelines.

## 💡 Better Alternative: Folder-based environments

We already use this pattern in our structure:

```
envs/
├── dev/
├── staging/
└── prod/
```

Each has its own:

* `backend.tf`
* `main.tf`
* Variable files
* Fully isolated state

This gives you **clarity, control, and cleaner CI/CD pipelines**.

## 🥊 Workspaces vs. Environments

!

> *TL;DR: Workspaces are great for quick testing,&#x20;****but folder-based environments win in real projects****.*

## ✅ Terraform Best Practices (Learned the Hard Way)

Terraform can be a joy or a headache — and sometimes both at once. These best practices are born out of *real-life scar tissue*. Save yourself the pain:

## 1. Use Modules, but Don’t Abuse Them

Modules are great. But not everything needs to be modularized. Don’t wrap a single S3 bucket in a module unless you’re reusing it — or unless you’re being paid by the module 😄

> ***Rule of thumb:****&#x20;If you use it in 2+ places, make it a module.*

## 2. Keep Environments Isolated

We already touched on this, but it’s worth repeating:

* One backend per environment
* One state file per team
* No shared “default” workspace for anything production-critical

## 3. Name Everything Consistently

Terraform doesn’t care what you name things, but your team will. Use a naming convention like:

```
resource "aws_instance" "web" {
  tags = {
    Name = "${var.env}-web-${count.index}"
  }
}
```

> `dev-web-0`*,&#x20;*`prod-web-2`*&#x20;— now&#x20;*&#x74;hat’&#x73;*&#x20;predictable chaos.*

## 4. Pin Your Provider Versions

Terraform upgrades can break your code. Lock versions in `required_providers` and `terraform` blocks:

```
terraform {
  required_version = "~> 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}
```

## 5. Use Remote State with Locking

Use backends like **S3 + DynamoDB** (on AWS) or **Terraform Cloud** for team projects. Never keep state in your local machine unless you enjoy surprises in production.

## 6. Automate with CI/CD

Integrate Terraform with GitLab CI, GitHub Actions, or whatever you use. Always run:

* `terraform fmt`
* `terraform validate`
* `terraform plan`

As part of your pipeline — even if it’s just to catch that one forgotten comma 😅

## 7. Avoid Hardcoded Secrets

Use environment variables, secret managers (like AWS Secrets Manager, Vault), or Terraform’s `sensitive = true`.

Never do this:

```
variable "db_password" {
  default = "hunter2"
}
```

Unless you like surprises on GitHub 😬

## 🕳️ Common Pitfalls in Terraform (a.k.a. “Things I Wish Someone Warned Me About”)

Even experienced Terraform users fall into these traps. Let’s save you the trouble:

## ⚠️ 1. Overengineering With Modules

> *“Look, I turned every resource into a module… and now I need a PhD to change a security group.”*

Don’t build a module to launch *just one* EC2 instance or a bucket unless it’s reused. Keep it **simple and meaningful**.

## ⚠️ 2. Relying Too Much on Workspaces

Workspaces feel convenient… until you’re trying to debug a production outage and realize you’re still in the `dev` workspace 🤦

> *Stick to folder-based environments unless you’re prototyping or playing.*

## ⚠️ 3. Forgetting to Lock Remote State

> *“Who applied last?” — A terrifying question.*

If you’re using a remote backend like S3, **enable locking** (e.g., with DynamoDB). Otherwise, two people can `terraform apply` at the same time, and now no one knows what’s deployed.

## ⚠️ 4. Ignoring `terraform plan`

Never `terraform apply` blind. Always run `terraform plan`, especially in CI/CD.

> *It’s like dry-run for your infrastructure… except it might save your job.*

## ⚠️ 5. Hardcoding Region, AMI IDs, etc.

```
provider "aws" {
  region = "us-east-1"
}
```

Nice — until you want to deploy to `eu-west-3`.

Use variables for region, environment, and other settings. Better yet, create a `locals.tf` file per environment.

## ⚠️ 6. Not Versioning Modules or Providers

Dependencies move fast. One day your build breaks because the AWS provider updated a deprecated field.

Use `~>` in version constraints. Lock your module sources to specific commits or versions if using `source = "git::..."`.

## ⚠️ 7. Ignoring Drift

> *“But I didn’t change anything!”\
> Yes… but someone&#x20;*&#x64;i&#x64;*&#x20;through the console.*

Use `terraform plan` regularly to detect *drift*. Tools like `terraform plan -detailed-exitcode` can help automate this in CI/CD.

## 🎁 Bonus Pitfall: Deleting State Files

> *“I wanted to start fresh…”*

Nope. Don’t. Ever.

Deleting the `.tfstate` file is like throwing away your car's steering wheel and hoping for the best. Use `terraform destroy` properly, or manage state cleanly via CLI/backends.

## 🧘 Final Thoughts: Terraform Is a Journey, Not Just a Tool

Structuring your Terraform projects well isn’t just about impressing your future self (though, trust me, you will). It’s about:

* Keeping your infrastructure scalable 🌱
* Helping teammates navigate your codebase 🧭
* Avoiding late-night production disasters 💥

You don’t have to get it perfect from the start. Terraform code evolves — and that’s okay. The key is to **start with structure in mind**, build reusable pieces over time, and make **clarity a priority**.

## 💡 TL;DR Recap:

* Use **modules** to keep code DRY — but don’t go overboard.
* Prefer **folder-based environments** over workspaces.
* Follow **best practices** and avoid common traps.
* Add **automation** where you can — Terraform loves CI/CD.
* Keep things **readable and version-controlled**.

## 🚀 Your Turn

If you’re starting a new Terraform project, try using the project structure and tips from this article. Or go refactor an old one — your teammates (and your future self) will thank you.

Got questions, feedback, or Terraform horror stories of your own? I’d love to hear them — drop a comment 👋

[Terraform](/tag/terraform?source=post_page-----92c3f47df02b---------------------------------------)

[DevOps](/tag/devops?source=post_page-----92c3f47df02b---------------------------------------)

[Iac](/tag/iac?source=post_page-----92c3f47df02b---------------------------------------)

[AWS](/tag/aws?source=post_page-----92c3f47df02b---------------------------------------)

[Cloud Architecture](/tag/cloud-architecture?source=post_page-----92c3f47df02b---------------------------------------)

[![Bouachirhamza](https://miro.medium.com/v2/resize:fill:96:96/1*yDPs6Tll8wfuDLUolF-h7g.jpeg)](/@bouachirhamza?source=post_page---post_author_info--92c3f47df02b---------------------------------------)

[![Bouachirhamza](https://miro.medium.com/v2/resize:fill:128:128/1*yDPs6Tll8wfuDLUolF-h7g.jpeg)](/@bouachirhamza?source=post_page---post_author_info--92c3f47df02b---------------------------------------)

## [Written by Bouachirhamza](/@bouachirhamza?source=post_page---post_author_info--92c3f47df02b---------------------------------------)

[84 followers](/@bouachirhamza/followers?source=post_page---post_author_info--92c3f47df02b---------------------------------------)

[77 following](/@bouachirhamza/following?source=post_page---post_author_info--92c3f47df02b---------------------------------------)

DevOps & Cloud engineer passionate about automation, CI/CD, Terraform, and cloud best practices. Here to share, learn, and build!

---

Powered by [curl.md](https://curl.md)