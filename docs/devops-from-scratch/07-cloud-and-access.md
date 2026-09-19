# 7. Cloud and access

## What "the cloud" is

Renting computers from someone else, by the hour, over the internet, instead of
buying and running your own. **Azure** (Microsoft) and **AWS** (Amazon) are the
two big ones you will see in job posts. **GCP** is Google's.

You do not learn the cloud by memorising every service. You learn a handful of
building blocks, and each provider just gives them different names.

## The building blocks

| Building block | Plain meaning | Azure | AWS |
|---|---|---|---|
| **Virtual machine (VM)** | A rented computer you can log in to | Virtual Machine | EC2 |
| **Storage** | A place to keep files and data, cheaply | Blob Storage | S3 |
| **Network** | A private network for your resources | Virtual Network (VNet) | VPC |
| **Kubernetes** | Managed Kubernetes | AKS | EKS |
| **Monitoring** | Metrics, logs and alerts | Azure Monitor | CloudWatch |
| **Secrets** | A vault for passwords and keys | Key Vault | Secrets Manager |
| **Identity and permissions** | Who is allowed to do what | Microsoft Entra ID and Azure RBAC | IAM |
| **Managed database** | A database someone else runs for you | Azure Database / Azure SQL | RDS |

Once you know "VM, storage, network", the job posting line "basic
understanding of Virtual Machines, Storage, Networking" is covered in
principle.

### Networking in one paragraph

Resources live in a private **network**, split into **subnets**. A **firewall**
(Azure: network security group, AWS: security group) is a list of rules about
what traffic may come in. Traffic reaches a service through a **port**, a
numbered door. This dashboard listens on port `8501`, which is why you open
`localhost:8501`. Only open the doors you need.

### Scaling

**Auto-scaling** adds more copies or bigger machines when load rises and removes
them when it falls, so you are not paying for idle capacity or falling over at
peak. `k8s/hpa.yaml` is a small example: keep between 2 and 5 pods, add more
when average CPU passes 70%.

## Infrastructure as code

Clicking around a cloud console to build things is slow and impossible to
repeat exactly. **Infrastructure as code** means writing the setup in files.
**Terraform** is the most common tool: you describe the database, the network,
the secret, and Terraform builds it.

Look at [`infra/aws/main.tf`](../../infra/aws/main.tf). You will see `resource`
blocks: a database, a secret, a container service. There are matching files for
Azure and GCP in `infra/`. **None of this has ever been applied to a real
account.** It shows the shape of the work.

## Access: IAM and RBAC

The most important security idea: **least privilege**. Every person and every
program gets only the access their job needs, nothing more.

Words:

- **Identity:** who or what is asking (a person, a service, a program).
- **Permission:** one allowed action, like "read this table".
- **Role:** a bundle of permissions with a name, like "Reader".
- **IAM** (AWS) and **RBAC** (Azure, "role-based access control") are the systems
  that assign roles to identities.

### How this project applies it

Read [`docs/security-rbac.md`](../security-rbac.md). The layers:

1. **A read-only database role** ([`infra/rbac/readonly_role.sql`](../../infra/rbac/readonly_role.sql)):
   the dashboard can `SELECT` and nothing else. Even a bug cannot delete data,
   because the database itself refuses.
2. **An application guard** in `connectors/warehouse.py`: blocks non-read
   queries and logs the attempt.
3. **Secrets in a vault**, never in code or in the image.
4. **The container runs as a non-root user** with no extra powers.

Why two layers guarding writes? Any single layer can have a bug. The
database role is the real lock, the application guard is the early warning.
This is called **defence in depth**.

### Compliance checks

The job mentions "access management and compliance checks". In plain terms: on
a schedule, prove that access is what it should be. Who has which role? Is any
password sitting in the code? The three-step review at the bottom of the
security doc is a tiny version of that.

## The AZ-900 certification

The job lists **AZ-900 (Azure Fundamentals)** as "good to have". It is an
entry-level exam about exactly the ideas on this page: what the cloud is,
core Azure services, security, and pricing. Microsoft publishes a free
learning path for it on their Microsoft Learn site. You can also make a free
Azure account to click around, which you would need to create yourself. Do not
enter card details anywhere you are not comfortable with. Reading the free
material is a good use of a weekend.

## Try it

1. Open [`infra/aws/main.tf`](../../infra/aws/main.tf) and find the `resource`
   block for the secret. Notice the database password is a variable, never
   typed in the file. Then open `infra/azure/main.tf` and find the equivalent
   pieces. Names differ, ideas match.
2. Run the blocked-query proof from the project root:

   ```bash
   python -c "from connectors.warehouse import run_query; run_query('DROP TABLE users')"
   ```

   You get an error saying only read-only statements are allowed. Now see it in
   the log:

   ```bash
   grep blocked logs/queries.jsonl | tail -1
   ```

   That is the application guard working and leaving evidence.
3. Write down, for each of the 4 access layers above, what it stops. Say it out
   loud.

## Check yourself

- What is least privilege, in one sentence?
- What is the Azure name for an AWS S3 bucket? For EC2? For CloudWatch?
- Why guard writes in two places?
- What is Terraform for, and has it been applied here?
