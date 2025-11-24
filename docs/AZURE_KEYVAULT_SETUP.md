# Azure Key Vault Setup Guide

This guide explains how to migrate from `.env` file secrets to Azure Key Vault for production deployments.

## Overview

Azure Key Vault provides centralized, secure storage for application secrets. This implementation:
- Eliminates hardcoded secrets in code/configuration files
- Uses `DefaultAzureCredential` for authentication (Managed Identity in production, Azure CLI locally)
- Supports secret rotation without code changes
- Provides audit trail for secret access

## Prerequisites

- Azure CLI installed (`az --version`)
- Logged in to Azure (`az login`)
- Appropriate Azure subscription permissions
- Factory Agent project cloned

## Step 1: Create Azure Key Vault

### Option A: Azure Portal

1. Navigate to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource" → Search "Key Vault"
3. Fill in details:
   - **Resource Group**: Same as your Container Apps (e.g., `factory-agent-rg`)
   - **Key Vault Name**: `factory-agent-kv` (must be globally unique)
   - **Region**: Same as your Container Apps
   - **Pricing Tier**: Standard (sufficient for most use cases)
4. Click "Review + Create" → "Create"

### Option B: Azure CLI

```bash
# Set variables
RESOURCE_GROUP="factory-agent-rg"
VAULT_NAME="factory-agent-kv"
LOCATION="eastus"  # Match your Container Apps region

# Create Key Vault
az keyvault create \
  --name $VAULT_NAME \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION \
  --enable-rbac-authorization true

# Get the vault URL (you'll need this later)
az keyvault show \
  --name $VAULT_NAME \
  --query properties.vaultUri \
  --output tsv
```

## Step 2: Configure Access Permissions

### For Local Development (Azure CLI Authentication)

```bash
# Get your user object ID
USER_ID=$(az ad signed-in-user show --query id --output tsv)

# Assign Key Vault Secrets User role to yourself
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee $USER_ID \
  --scope "/subscriptions/<subscription-id>/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$VAULT_NAME"
```

### For Production (Managed Identity)

If deploying to Azure Container Apps:

```bash
# Get the Managed Identity ID from your Container App
IDENTITY_ID=$(az containerapp show \
  --name factory-agent-backend \
  --resource-group $RESOURCE_GROUP \
  --query identity.principalId \
  --output tsv)

# Assign Key Vault Secrets User role to Managed Identity
az role assignment create \
  --role "Key Vault Secrets User" \
  --assignee $IDENTITY_ID \
  --scope "/subscriptions/<subscription-id>/resourceGroups/$RESOURCE_GROUP/providers/Microsoft.KeyVault/vaults/$VAULT_NAME"
```

## Step 3: Upload Secrets to Key Vault

### Option A: Using the Helper Script (Recommended)

```bash
# Make script executable
chmod +x scripts/upload_secrets_to_keyvault.sh

# Run the script
./scripts/upload_secrets_to_keyvault.sh factory-agent-kv
```

The script automatically:
- Reads secrets from your `.env` file
- Converts environment variable names to Key Vault format (e.g., `AZURE_API_KEY` → `AZURE-API-KEY`)
- Uploads only non-empty, non-placeholder values
- Skips secrets that are already placeholder values

### Option B: Manual Upload

```bash
# Azure AI Foundry secrets
az keyvault secret set \
  --vault-name factory-agent-kv \
  --name AZURE-ENDPOINT \
  --value "https://your-resource.services.ai.azure.com"

az keyvault secret set \
  --vault-name factory-agent-kv \
  --name AZURE-API-KEY \
  --value "your-actual-api-key-here"

# Azure Storage secret
az keyvault secret set \
  --vault-name factory-agent-kv \
  --name AZURE-STORAGE-CONNECTION-STRING \
  --value "DefaultEndpointsProtocol=https;AccountName=..."

# Optional configuration
az keyvault secret set \
  --vault-name factory-agent-kv \
  --name AZURE-DEPLOYMENT-NAME \
  --value "gpt-4"

az keyvault secret set \
  --vault-name factory-agent-kv \
  --name AZURE-API-VERSION \
  --value "2024-08-01-preview"

az keyvault secret set \
  --vault-name factory-agent-kv \
  --name FACTORY-NAME \
  --value "Demo Factory"
```

## Step 4: Configure Application

### Local Development

Add to your `.env` file:

```bash
# Azure Key Vault Configuration
KEYVAULT_URL=https://factory-agent-kv.vault.azure.net/
```

Ensure you're logged in to Azure CLI:

```bash
az login
```

### Production Deployment

Update your Azure Container App environment variables:

```bash
# Set Key Vault URL as environment variable
az containerapp update \
  --name factory-agent-backend \
  --resource-group factory-agent-rg \
  --set-env-vars "KEYVAULT_URL=https://factory-agent-kv.vault.azure.net/"
```

## Step 5: Install Dependencies

```bash
# Navigate to backend directory
cd backend

# Install new dependencies
pip3 install azure-keyvault-secrets>=4.8.0 azure-identity>=1.15.0

# Or install all requirements
pip3 install -r requirements.txt
```

## Step 6: Test the Integration

### Test Locally

```bash
# Start the backend
cd backend
PYTHONPATH=/Users/willmacdonald/Documents/Code/azure/factory-agent:$PYTHONPATH \
  venv/bin/uvicorn src.api.main:app --reload
```

Check the logs for:
- `Azure Key Vault client initialized: https://factory-agent-kv.vault.azure.net/`
- `Successfully retrieved secret from Key Vault: AZURE-API-KEY`

### Test Secret Retrieval

```python
# Test in Python REPL
python3
>>> from shared.config import AZURE_API_KEY, AZURE_ENDPOINT
>>> print(f"Endpoint: {AZURE_ENDPOINT}")
>>> print(f"API Key loaded: {bool(AZURE_API_KEY)}")
```

## Secret Name Mapping

Azure Key Vault uses hyphens in secret names, not underscores:

| Environment Variable | Key Vault Secret Name |
|---------------------|---------------------|
| `AZURE_ENDPOINT` | `AZURE-ENDPOINT` |
| `AZURE_API_KEY` | `AZURE-API-KEY` |
| `AZURE_STORAGE_CONNECTION_STRING` | `AZURE-STORAGE-CONNECTION-STRING` |
| `AZURE_DEPLOYMENT_NAME` | `AZURE-DEPLOYMENT-NAME` |
| `AZURE_API_VERSION` | `AZURE-API-VERSION` |
| `FACTORY_NAME` | `FACTORY-NAME` |

## Troubleshooting

### "Failed to initialize Key Vault client"

**Cause**: `KEYVAULT_URL` not set or invalid

**Solution**:
```bash
# Check if KEYVAULT_URL is set
echo $KEYVAULT_URL

# Verify the vault exists
az keyvault show --name factory-agent-kv
```

### "Failed to retrieve secret from Key Vault: (Forbidden)"

**Cause**: Missing permissions on Key Vault

**Solution**:
```bash
# Check your permissions
az role assignment list \
  --scope "/subscriptions/<subscription-id>/resourceGroups/factory-agent-rg/providers/Microsoft.KeyVault/vaults/factory-agent-kv"

# Add Key Vault Secrets User role (see Step 2)
```

### "Key Vault not configured, cannot retrieve secret"

**Cause**: `KEYVAULT_URL` not set in environment

**Solution**: Add `KEYVAULT_URL` to `.env` file or export it:
```bash
export KEYVAULT_URL=https://factory-agent-kv.vault.azure.net/
```

### Secrets Not Loading

**Check**:
1. Key Vault URL is correct (includes `https://` and trailing `/`)
2. Secret names use hyphens, not underscores
3. You have "Key Vault Secrets User" role (not "Reader")
4. You're logged in to Azure CLI (`az login`)

## Security Best Practices

1. **Never commit `.env` to git**: Ensure `.env` is in `.gitignore`
2. **Rotate secrets regularly**: Update secrets in Key Vault, not code
3. **Use Managed Identity in production**: Avoid storing credentials
4. **Limit Key Vault permissions**: Only grant "Secrets User", not "Officer"
5. **Enable auditing**: Use Azure Monitor to track secret access

## Updating Secrets

To update a secret:

```bash
# Update secret value
az keyvault secret set \
  --vault-name factory-agent-kv \
  --name AZURE-API-KEY \
  --value "new-api-key-value"

# Restart application to pick up new value
az containerapp revision restart \
  --name factory-agent-backend \
  --resource-group factory-agent-rg
```

## Removing Key Vault Integration

To revert to `.env` file only:

1. Remove or comment out `KEYVAULT_URL` from `.env`:
   ```bash
   # KEYVAULT_URL=https://factory-agent-kv.vault.azure.net/
   ```

2. Ensure all secrets are in `.env` file:
   ```bash
   AZURE_ENDPOINT=your-endpoint
   AZURE_API_KEY=your-key
   AZURE_STORAGE_CONNECTION_STRING=your-connection-string
   ```

3. Restart the application

The application will automatically fall back to using environment variables when Key Vault is not configured.

## Cost Considerations

Azure Key Vault pricing (Standard tier):
- **Secret operations**: $0.03 per 10,000 transactions
- **Secrets stored**: First 1,000 secrets included

For Factory Agent:
- ~6 secrets stored
- ~10-20 secret retrievals per application start
- **Estimated monthly cost**: < $0.10

## References

- [Azure Key Vault Documentation](https://learn.microsoft.com/en-us/azure/key-vault/)
- [DefaultAzureCredential Documentation](https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential)
- [Azure RBAC for Key Vault](https://learn.microsoft.com/en-us/azure/key-vault/general/rbac-guide)
