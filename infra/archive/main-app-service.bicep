// =============================================================================
// Azure App Service Infrastructure for Factory Agent
// =============================================================================
// Simpler alternative to Container Apps - more mature, fewer deployment issues

targetScope = 'resourceGroup'

// =============================================================================
// PARAMETERS
// =============================================================================

@description('Application name (used as prefix for all resources)')
@minLength(3)
@maxLength(20)
param appName string = 'factory-agent'

@description('Azure region for resources')
param location string = resourceGroup().location

@description('Environment name')
@allowed([
  'dev'
  'staging'
  'prod'
])
param environmentName string = 'dev'

@description('Container image tag (e.g., latest, v1.0.0, or commit SHA)')
param imageTag string = 'latest'

@description('Azure OpenAI endpoint URL')
@secure()
param azureOpenAiEndpoint string

@description('Azure OpenAI API key')
@secure()
param azureOpenAiKey string

@description('Azure OpenAI deployment name (model deployment)')
param azureOpenAiDeployment string = 'gpt-4'

@description('Azure OpenAI API version')
param azureOpenAiApiVersion string = '2024-02-15-preview'

@description('Storage mode: local or blob')
@allowed([
  'local'
  'blob'
])
param storageMode string = 'blob'

@description('Azure Storage connection string (required if storageMode=blob)')
@secure()
param azureStorageConnectionString string = ''

@description('Azure Storage container name (required if storageMode=blob)')
param azureStorageContainerName string = 'factory-data'

// =============================================================================
// VARIABLES
// =============================================================================

var resourceNamePrefix = '${appName}-${environmentName}'
var appServicePlanName = '${resourceNamePrefix}-plan'
var appServiceName = '${resourceNamePrefix}-backend'

// ACR name (created by deploy.sh via CLI, passed as parameter would be cleaner but this matches CLI logic)
// Note: We can't replicate bash sha256sum in Bicep, so deploy.sh will pass the actual ACR name
@description('Container Registry name (auto-detected or created by deploy.sh)')
param containerRegistryName string

// =============================================================================
// RESOURCES
// =============================================================================

// -----------------------------------------------------------------------------
// App Service Plan (Linux + Docker)
// -----------------------------------------------------------------------------
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: appServicePlanName
  location: location
  kind: 'linux'
  sku: {
    name: 'F1'                       // Free tier - no quota restrictions, no cost
    tier: 'Free'
  }
  properties: {
    reserved: true                   // Required for Linux
  }
  tags: {
    environment: environmentName
    application: appName
  }
}

// -----------------------------------------------------------------------------
// App Service (Docker Container)
// -----------------------------------------------------------------------------
resource appService 'Microsoft.Web/sites@2023-01-01' = {
  name: appServiceName
  location: location
  kind: 'app,linux,container'
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'DOCKER|${containerRegistryName}.azurecr.io/${appName}/backend:${imageTag}'
      alwaysOn: false                // Set to false for Basic tier (true requires Standard+)
      appSettings: [
        {
          name: 'WEBSITES_ENABLE_APP_SERVICE_STORAGE'
          value: 'false'
        }
        {
          name: 'DOCKER_REGISTRY_SERVER_URL'
          value: 'https://${containerRegistryName}.azurecr.io'
        }
        {
          name: 'DOCKER_ENABLE_CI'
          value: 'true'
        }
        // Application settings
        {
          name: 'AZURE_OPENAI_ENDPOINT'
          value: azureOpenAiEndpoint
        }
        {
          name: 'AZURE_OPENAI_KEY'
          value: azureOpenAiKey
        }
        {
          name: 'AZURE_OPENAI_DEPLOYMENT'
          value: azureOpenAiDeployment
        }
        {
          name: 'AZURE_OPENAI_API_VERSION'
          value: azureOpenAiApiVersion
        }
        {
          name: 'STORAGE_MODE'
          value: storageMode
        }
        {
          name: 'AZURE_STORAGE_CONNECTION_STRING'
          value: azureStorageConnectionString
        }
        {
          name: 'AZURE_STORAGE_CONTAINER_NAME'
          value: azureStorageContainerName
        }
        {
          name: 'PORT'
          value: '8000'              // FastAPI default port
        }
      ]
      cors: {
        allowedOrigins: [
          '*'                        // Allow all origins for demo (restrict in production)
        ]
        supportCredentials: false
      }
    }
  }
  identity: {
    type: 'SystemAssigned'           // Managed Identity for ACR pull
  }
  tags: {
    environment: environmentName
    application: appName
  }
}

// -----------------------------------------------------------------------------
// Role Assignment: App Service → ACR Pull
// -----------------------------------------------------------------------------
// Note: ACR is created via CLI in deploy.sh, we reference it here for role assignment
resource existingAcr 'Microsoft.ContainerRegistry/registries@2023-07-01' existing = {
  name: containerRegistryName
}

resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(existingAcr.id, appService.id, 'AcrPull')
  scope: existingAcr
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d') // AcrPull role
    principalId: appService.identity.principalId
    principalType: 'ServicePrincipal'
  }
}

// =============================================================================
// OUTPUTS
// =============================================================================

output backendUrl string = 'https://${appService.properties.defaultHostName}'
output appServiceName string = appService.name
output appServicePlanName string = appServicePlan.name
output containerRegistryName string = containerRegistryName
