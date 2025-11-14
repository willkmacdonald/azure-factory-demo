// =============================================================================
// Bicep Parameters File for Factory Agent Deployment
// =============================================================================
// This file provides parameter values for the main.bicep template.
//
// Usage:
//   az deployment group create \
//     --resource-group factory-agent-rg \
//     --template-file main.bicep \
//     --parameters main.bicepparam
//
// For production deployments, consider using separate parameter files:
// - main-dev.bicepparam
// - main-staging.bicepparam
// - main-prod.bicepparam
// =============================================================================

using './main.bicep'

// =============================================================================
// APPLICATION CONFIGURATION
// =============================================================================

param appName = 'factory-agent'
param environmentName = 'dev'
param imageTag = 'latest'

// =============================================================================
// AZURE OPENAI CONFIGURATION
// =============================================================================
// IMPORTANT: Replace these with your actual Azure OpenAI values
// For security, consider using Azure Key Vault references instead:
// param azureOpenAiKey = getSecret('key-vault-name', 'openai-key-secret')

param azureOpenAiEndpoint = '<YOUR_AZURE_OPENAI_ENDPOINT>'
param azureOpenAiKey = '<YOUR_AZURE_OPENAI_KEY>'
param azureOpenAiDeployment = 'gpt-4'
param azureOpenAiApiVersion = '2024-02-15-preview'

// =============================================================================
// STORAGE CONFIGURATION
// =============================================================================

param storageMode = 'blob'
param azureStorageConnectionString = '<YOUR_AZURE_STORAGE_CONNECTION_STRING>'
param azureStorageContainerName = 'factory-data'

// =============================================================================
// NETWORKING CONFIGURATION
// =============================================================================

// For development: Allow all origins
// For production: Replace with your frontend domain
// Example: 'https://factory-agent.com,https://www.factory-agent.com'
param allowedOrigins = '*'

// =============================================================================
// SCALING CONFIGURATION
// =============================================================================

// Development: Scale to zero when idle (cost savings)
param minReplicas = 0
param maxReplicas = 3

// Development: Smaller resource allocation
param cpuCores = '0.5'
param memorySize = '1.0'

// =============================================================================
// PRODUCTION OVERRIDES (uncomment for production deployments)
// =============================================================================

// Production scaling: Always have 1 instance running (better performance)
// param minReplicas = 1
// param maxReplicas = 10

// Production resources: More CPU and memory for better performance
// param cpuCores = '1.0'
// param memorySize = '2.0'

// Production CORS: Restrict to your frontend domain
// param allowedOrigins = 'https://factory-agent.com,https://www.factory-agent.com'
