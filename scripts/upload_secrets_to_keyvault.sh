#!/bin/bash
# Upload secrets from .env file to Azure Key Vault
# Usage: ./scripts/upload_secrets_to_keyvault.sh <vault-name>
#
# Prerequisites:
# - Azure CLI installed and logged in (az login)
# - Appropriate permissions on the Key Vault (Key Vault Secrets Officer role)
# - .env file exists in project root

set -e  # Exit on error

# Check if vault name provided
if [ -z "$1" ]; then
    echo "Error: Vault name required"
    echo "Usage: $0 <vault-name>"
    echo "Example: $0 factory-agent-kv"
    exit 1
fi

VAULT_NAME="$1"
ENV_FILE=".env"

# Check if .env file exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found in current directory"
    exit 1
fi

echo "============================================"
echo "Uploading secrets to Azure Key Vault"
echo "Vault: $VAULT_NAME"
echo "============================================"

# Function to upload secret
upload_secret() {
    local secret_name="$1"
    local secret_value="$2"

    if [ -n "$secret_value" ] && [ "$secret_value" != "your-"* ]; then
        echo "Uploading: $secret_name"
        az keyvault secret set \
            --vault-name "$VAULT_NAME" \
            --name "$secret_name" \
            --value "$secret_value" \
            --output none
        echo "  ✓ $secret_name uploaded"
    else
        echo "  ⊘ Skipping $secret_name (empty or placeholder value)"
    fi
}

# Source .env and upload critical secrets
# Note: Azure Key Vault uses hyphens in secret names, not underscores

echo ""
echo "Uploading Azure AI Foundry secrets..."
if grep -q "^AZURE_ENDPOINT=" "$ENV_FILE"; then
    VALUE=$(grep "^AZURE_ENDPOINT=" "$ENV_FILE" | cut -d '=' -f2-)
    upload_secret "AZURE-ENDPOINT" "$VALUE"
fi

if grep -q "^AZURE_API_KEY=" "$ENV_FILE"; then
    VALUE=$(grep "^AZURE_API_KEY=" "$ENV_FILE" | cut -d '=' -f2-)
    upload_secret "AZURE-API-KEY" "$VALUE"
fi

echo ""
echo "Uploading Azure Storage secrets..."
if grep -q "^AZURE_STORAGE_CONNECTION_STRING=" "$ENV_FILE"; then
    VALUE=$(grep "^AZURE_STORAGE_CONNECTION_STRING=" "$ENV_FILE" | cut -d '=' -f2-)
    upload_secret "AZURE-STORAGE-CONNECTION-STRING" "$VALUE"
fi

echo ""
echo "Uploading optional configuration..."
if grep -q "^AZURE_DEPLOYMENT_NAME=" "$ENV_FILE"; then
    VALUE=$(grep "^AZURE_DEPLOYMENT_NAME=" "$ENV_FILE" | cut -d '=' -f2-)
    upload_secret "AZURE-DEPLOYMENT-NAME" "$VALUE"
fi

if grep -q "^AZURE_API_VERSION=" "$ENV_FILE"; then
    VALUE=$(grep "^AZURE_API_VERSION=" "$ENV_FILE" | cut -d '=' -f2-)
    upload_secret "AZURE-API-VERSION" "$VALUE"
fi

if grep -q "^FACTORY_NAME=" "$ENV_FILE"; then
    VALUE=$(grep "^FACTORY_NAME=" "$ENV_FILE" | cut -d '=' -f2-)
    upload_secret "FACTORY-NAME" "$VALUE"
fi

echo ""
echo "============================================"
echo "✓ Secrets upload complete"
echo "============================================"
echo ""
echo "Next steps:"
echo "1. Set KEYVAULT_URL environment variable:"
echo "   export KEYVAULT_URL=https://$VAULT_NAME.vault.azure.net/"
echo ""
echo "2. Or add to .env file:"
echo "   KEYVAULT_URL=https://$VAULT_NAME.vault.azure.net/"
echo ""
echo "3. Ensure your Managed Identity or Service Principal has"
echo "   'Key Vault Secrets User' role on the vault"
echo ""
