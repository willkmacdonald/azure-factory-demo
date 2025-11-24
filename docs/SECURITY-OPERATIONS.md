# Security Operations Guide - Factory Agent

**Last Updated**: 2025-11-23
**Status**: PR24A Complete - No secrets found in git history

---

## Executive Summary

This document provides comprehensive security operations guidance for the Factory Agent project, including:
- API key rotation procedures
- Secret scanning results and remediation
- Credential management best practices
- Incident response procedures

---

## Secret Scanning Audit (2025-11-23)

### Tools Used
- **Gitleaks 8.29.1** - Industry-standard secret scanner
- Manual git history inspection
- Pattern-based searches for Azure credentials

### Scan Results

**Status**: ✅ **PASS - No secrets found in git history**

```
91 commits scanned
~3.01 MB of data analyzed
Scan duration: 254ms
Result: No leaks found
```

### Key Findings

1. ✅ `.env` file is properly in `.gitignore` (line 9)
2. ✅ `.env` file was NEVER committed to git history
3. ✅ No API keys found in git history
4. ✅ Only environment variable references found (no actual values)
5. ✅ `.mcp.json` also properly excluded (contains secrets)

### Files Verified in .gitignore

```gitignore
# Environment secrets
.env                    # Application secrets
.mcp.json              # MCP server secrets

# Deployment secrets
/infra/main-deploy.bicepparam
/DEPLOYMENT-SECRETS.md
DEPLOYMENT-RESUME.md
DEPLOYMENT-NEXT-STEPS.md
```

---

## Current Secrets Inventory

### Development Secrets (Local .env file)

**Location**: `.env` (NOT committed to git)

| Secret | Purpose | Rotation Frequency | Status |
|--------|---------|-------------------|--------|
| `AZURE_ENDPOINT` | Azure AI Foundry base endpoint | N/A (not secret) | ✅ Active |
| `AZURE_API_VERSION` | API version | N/A (not secret) | ✅ Active |
| `AZURE_STORAGE_CONNECTION_STRING` | Blob Storage access | Every 90 days | ⚠️ Needs rotation schedule |
| `DEEPCONTEXT_API_KEY` | DeepContext MCP service | Every 90 days | ⚠️ Needs rotation schedule |

**Note**: We use Azure AD authentication (DefaultAzureCredential) for Azure AI Foundry, eliminating the need for API keys in `.env`.

### Production Secrets (Azure Key Vault)

**Recommendation**: Migrate to Azure Key Vault for production deployment.

**Key Vault Setup**: See [docs/AZURE_KEYVAULT_SETUP.md](./AZURE_KEYVAULT_SETUP.md)

---

## API Key Rotation Procedures

### Azure AI Foundry (Recommended: Azure AD Authentication)

**Current Status**: ✅ Using DefaultAzureCredential (keyless authentication)

**Why Azure AD is Better**:
- No API keys to rotate
- Automatic token refresh
- Audit trail via Azure AD logs
- Fine-grained access control via RBAC

**If Using API Keys** (not recommended):
1. Navigate to Azure AI Foundry resource in Azure Portal
2. Select "Keys and Endpoint" tab
3. Click "Regenerate Key 2"
4. Update `.env` file with new key
5. Restart application
6. After verification, regenerate Key 1
7. Update production deployments

**Frequency**: Every 90 days (if using keys)

---

### Azure Blob Storage Connection String

**Method 1: Portal Rotation** (Manual)

```bash
# 1. Navigate to Storage Account in Azure Portal
# 2. Select "Access keys" under Security + networking
# 3. Click "Rotate key" for key2
# 4. Copy new connection string
# 5. Update .env file

# Connection string format:
# DefaultEndpointsProtocol=https;AccountName=<name>;AccountKey=<key>;EndpointSuffix=core.windows.net
```

**Method 2: Azure CLI** (Automated)

```bash
# Regenerate storage account key2
az storage account keys renew \
  --resource-group <resource-group-name> \
  --account-name <storage-account-name> \
  --key key2

# Get new connection string
az storage account show-connection-string \
  --resource-group <resource-group-name> \
  --name <storage-account-name> \
  --key key2 \
  --query connectionString \
  --output tsv
```

**Method 3: REST API** (For automation)

```bash
POST https://management.azure.com/subscriptions/{subscriptionId}/resourceGroups/{resourceGroupName}/providers/Microsoft.Storage/storageAccounts/{accountName}/regenerateKey?api-version=2023-01-01

Body:
{
  "keyName": "key2"
}
```

**Rotation Workflow** (Zero-downtime):

1. Regenerate key2
2. Update production environment variable to use key2
3. Restart application
4. Verify application works with key2
5. Regenerate key1 (old key invalidated)
6. Keep key2 as active, key1 as backup

**Frequency**: Every 90 days

---

### DeepContext API Key

**Method**: Regenerate via DeepContext service dashboard

1. Log in to DeepContext account
2. Navigate to API Keys section
3. Generate new API key
4. Update `.env` file:
   ```bash
   DEEPCONTEXT_API_KEY=<new-key-here>
   ```
5. Restart development environment
6. Revoke old API key in DeepContext dashboard

**Frequency**: Every 90 days

---

## Credential Management Best Practices

### Development Environment

**✅ Current Practice** (Good):
- `.env` file for local development secrets
- `.env.example` with placeholder values (committed to git)
- `.env` in `.gitignore`
- `python-dotenv` for loading environment variables

**Best Practices**:
1. **Never commit .env file**
   - Verify: `git log --all --full-history -- .env` (should be empty)
   - Use `.env.example` for documentation

2. **Use environment variable references in code**
   ```python
   # ✅ Good
   from shared.config import AZURE_STORAGE_CONNECTION_STRING

   # ❌ Bad - never hardcode
   connection_string = "DefaultEndpointsProtocol=https;AccountName=..."
   ```

3. **Validate secrets at startup**
   ```python
   @app.on_event("startup")
   async def validate_secrets():
       if not AZURE_STORAGE_CONNECTION_STRING:
           raise ValueError("AZURE_STORAGE_CONNECTION_STRING is required")
   ```

---

### Production Environment (Azure Container Apps)

**Recommended Approach**: Azure Key Vault + Managed Identity

```bicep
// 1. Create Key Vault
resource keyVault 'Microsoft.KeyVault/vaults@2023-07-01' = {
  name: 'factory-agent-kv'
  properties: {
    enabledForTemplateDeployment: true
    sku: { family: 'A', name: 'standard' }
    tenantId: subscription().tenantId
  }
}

// 2. Store secrets
resource storageSecret 'Microsoft.KeyVault/vaults/secrets@2023-07-01' = {
  parent: keyVault
  name: 'AzureStorageConnectionString'
  properties: {
    value: storageConnectionString
  }
}

// 3. Grant Container App access via Managed Identity
resource secretAccess 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  scope: keyVault
  properties: {
    roleDefinitionId: '/providers/Microsoft.Authorization/roleDefinitions/4633458b-17de-408a-b874-0445c86b69e6' // Key Vault Secrets User
    principalId: containerApp.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// 4. Reference in Container App
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  properties: {
    configuration: {
      secrets: [
        {
          name: 'azure-storage-connection'
          keyVaultUrl: '${keyVault.properties.vaultUri}secrets/AzureStorageConnectionString'
          identity: 'system'
        }
      ]
    }
    template: {
      containers: [{
        env: [{
          name: 'AZURE_STORAGE_CONNECTION_STRING'
          secretRef: 'azure-storage-connection'
        }]
      }]
    }
  }
}
```

**Benefits**:
- Centralized secret management
- Automatic secret refresh (configurable interval)
- Audit trail for secret access
- No secrets in container images or source code

---

## Secret Scanning Tools

### Gitleaks (Recommended)

**Installation**:
```bash
brew install gitleaks
```

**Scan Entire Git History**:
```bash
gitleaks detect --source . --verbose
```

**Scan Uncommitted Changes** (Pre-commit hook):
```bash
gitleaks protect --staged --verbose
```

**Add as Pre-commit Hook**:
```bash
# .git/hooks/pre-commit
#!/bin/sh
gitleaks protect --staged --verbose
```

### Alternative Tools

- **TruffleHog**: 800+ secret types, active verification
- **detect-secrets**: Enterprise-friendly, minimal false positives
- **GitHub Secret Scanning**: Native GitHub integration (free for public repos)

---

## Incident Response Procedures

### If Secrets are Exposed in Git History

**Severity**: CRITICAL

**Immediate Actions** (within 1 hour):

1. **Rotate ALL exposed secrets immediately**
   - Azure Storage keys
   - Azure AI Foundry keys (if used)
   - Any third-party API keys
   - Document rotation timestamps

2. **Verify git history**
   ```bash
   # Check if secret is in git history
   git log --all --full-history -- .env
   git log --all -p -S "AZURE_STORAGE_CONNECTION_STRING"
   ```

3. **Remove from git history** (if found)
   ```bash
   # Option 1: BFG Repo-Cleaner (recommended)
   brew install bfg
   bfg --delete-files .env
   git reflog expire --expire=now --all
   git gc --prune=now --aggressive

   # Option 2: git-filter-repo
   git filter-repo --invert-paths --path .env

   # Force push (⚠️ Requires team coordination)
   git push origin --force --all
   ```

4. **Audit access logs**
   - Check Azure Activity Logs for unauthorized access
   - Check storage account access logs
   - Document timeline of exposure

5. **Notify stakeholders**
   - Security team (if enterprise)
   - Project maintainers
   - Document incident in SECURITY.md

**Follow-up Actions** (within 24 hours):

6. **Add secret scanning to CI/CD**
   ```yaml
   # .github/workflows/security-scan.yml
   name: Secret Scan
   on: [push, pull_request]
   jobs:
     gitleaks:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v4
           with:
             fetch-depth: 0
         - uses: gitleaks/gitleaks-action@v2
   ```

7. **Review .gitignore**
   - Ensure all secret files are excluded
   - Test with `git status` and dry-run commits

8. **Educate team**
   - Share incident post-mortem
   - Review best practices
   - Update documentation

---

### If Secrets are Exposed Publicly

**Severity**: CRITICAL

**Additional Actions**:

1. **GitHub Actions**: Revoke exposed GitHub secrets
2. **Azure Portal**: Review all recent API calls in Azure Activity Log
3. **Monitor billing**: Check for unauthorized usage
4. **Consider Key Vault**: Migrate to Azure Key Vault immediately

---

## Automated Secret Rotation (Future Enhancement)

### Azure Function for Automated Rotation

```python
import azure.functions as func
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient

def rotate_storage_key(resource_group: str, account_name: str, key_vault_name: str):
    """Rotate storage account key and update Key Vault secret."""

    # 1. Regenerate storage key2
    storage_client = StorageManagementClient(DefaultAzureCredential(), subscription_id)
    storage_client.storage_accounts.regenerate_key(
        resource_group_name=resource_group,
        account_name=account_name,
        regenerate_key_parameters={"keyName": "key2"}
    )

    # 2. Get new connection string
    keys = storage_client.storage_accounts.list_keys(resource_group, account_name)
    new_connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={keys.keys[1].value};EndpointSuffix=core.windows.net"

    # 3. Update Key Vault secret
    kv_client = SecretClient(vault_url=f"https://{key_vault_name}.vault.azure.net", credential=DefaultAzureCredential())
    kv_client.set_secret("AzureStorageConnectionString", new_connection_string)

    return f"Rotated storage key2 for {account_name}"

def main(mytimer: func.TimerRequest) -> None:
    """Azure Function triggered every 90 days."""
    rotate_storage_key("factory-agent-rg", "factoryagentdata", "factory-agent-kv")
```

### GitHub Actions for Rotation Reminders

```yaml
name: Secret Rotation Reminder
on:
  schedule:
    - cron: '0 0 1 */3 *'  # Every 3 months

jobs:
  rotation-reminder:
    runs-on: ubuntu-latest
    steps:
      - name: Create GitHub Issue
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.create({
              owner: context.repo.owner,
              repo: context.repo.repo,
              title: 'Security: Rotate API Keys and Secrets',
              body: 'Quarterly secret rotation due. See docs/SECURITY-OPERATIONS.md for procedures.',
              labels: ['security', 'maintenance']
            })
```

---

## Compliance Checklist

### Before Public Repository

- [ ] `.env` file NOT in git history (verified with gitleaks)
- [ ] `.env` in `.gitignore` (verified)
- [ ] No API keys in source code (verified)
- [ ] `.env.example` has placeholders only (no real values)
- [ ] All secrets rotated recently (<90 days)
- [ ] Secret scanning in CI/CD pipeline (optional but recommended)
- [ ] Production uses Azure Key Vault (recommended for deployment)

### Before Production Deployment

- [ ] Migrate to Azure Key Vault
- [ ] Enable Managed Identity for Container Apps
- [ ] Configure secret refresh interval (recommended: 2 hours)
- [ ] Set up automated rotation (Azure Function)
- [ ] Enable audit logging for secret access
- [ ] Document rotation procedures for team
- [ ] Test secret rotation in staging environment

---

## References

### Azure Documentation

- [Azure AI Services - Rotate Keys](https://learn.microsoft.com/en-us/azure/ai-services/rotate-keys)
- [Azure Key Vault Best Practices](https://learn.microsoft.com/en-us/azure/key-vault/general/best-practices)
- [Azure Storage Account Key Management](https://learn.microsoft.com/en-us/azure/storage/common/storage-account-keys-manage)

### Security Tools

- [Gitleaks](https://github.com/gitleaks/gitleaks) - Open-source secret scanner
- [TruffleHog](https://github.com/trufflesecurity/trufflehog) - Find and verify secrets
- [detect-secrets](https://github.com/Yelp/detect-secrets) - Prevent secrets in code

### Industry Standards

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [NIST SP 800-57 Key Management](https://csrc.nist.gov/publications/detail/sp/800-57-part-1/rev-5/final)

---

## Appendix: PR24A Audit Summary

**Date**: 2025-11-23
**Auditor**: Claude Code (Automated)
**Scope**: Full git history scan for exposed secrets

### Audit Steps Performed

1. ✅ Verified `.env` in `.gitignore`
2. ✅ Searched git history for `.env` file commits
3. ✅ Searched git history for `*.env` pattern
4. ✅ Searched commit messages for API key references
5. ✅ Ran gitleaks scanner on entire repository
6. ✅ Manual inspection of Azure-related commits

### Findings

- **Result**: NO SECRETS FOUND
- **Commits Scanned**: 91
- **Data Analyzed**: ~3.01 MB
- **Files Checked**: All tracked files across all branches
- **Pattern Matches**: None

### Recommendations

1. ✅ No immediate key rotation required (no exposure detected)
2. ⚠️ Implement rotation schedule (every 90 days)
3. ✅ Add gitleaks pre-commit hook (optional but recommended)
4. ⚠️ Migrate to Azure Key Vault before public deployment

**Status**: PASS - Repository is secure for public sharing

---

**Document Version**: 1.0
**Next Review**: Before production deployment
**Owner**: Factory Agent Security Team
