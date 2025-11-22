// =============================================================================
// Shared Infrastructure for Factory Agent - Azure Container Apps
// =============================================================================
// This Bicep module creates shared resources used by both backend and frontend:
// - Log Analytics Workspace (centralized logging)
// - Container Apps Environment (runtime environment for both apps)
// - Managed Identity (for ACR access)
//
// Deploy this template ONCE or when shared infrastructure changes.
// Backend and frontend deployments reference these resources.
//
// Deployment:
//   az deployment group create \
//     --resource-group <rg-name> \
//     --template-file shared.bicep \
//     --parameters environmentName=dev
// =============================================================================

// =============================================================================
// PARAMETERS
// =============================================================================

@description('Name of the application (used as prefix for all resources)')
param appName string = 'factory-agent'

@description('Azure region for all resources')
param location string = resourceGroup().location

@description('Environment name (dev, staging, prod)')
@allowed([
  'dev'
  'staging'
  'prod'
])
param environmentName string = 'dev'

@description('Existing Azure Container Registry name (without .azurecr.io)')
@minLength(5)
@maxLength(50)
param containerRegistryName string = 'factoryagent4u4zqkacr'

// =============================================================================
// VARIABLES
// =============================================================================

var resourceNamePrefix = '${appName}-${environmentName}'
var logAnalyticsName = '${resourceNamePrefix}-logs'
var containerEnvName = '${resourceNamePrefix}-env'
var managedIdentityName = '${resourceNamePrefix}-identity'

// =============================================================================
// RESOURCES
// =============================================================================

// -----------------------------------------------------------------------------
// User-Assigned Managed Identity
// -----------------------------------------------------------------------------
// Shared identity used by both backend and frontend for ACR access
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: managedIdentityName
  location: location
  tags: {
    environment: environmentName
    application: appName
    component: 'shared'
  }
}

// -----------------------------------------------------------------------------
// Log Analytics Workspace
// -----------------------------------------------------------------------------
// Centralized logging for all Container Apps
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
  tags: {
    environment: environmentName
    application: appName
    component: 'shared'
  }
}

// -----------------------------------------------------------------------------
// Container Apps Environment
// -----------------------------------------------------------------------------
// Shared runtime environment for backend and frontend Container Apps
resource containerEnv 'Microsoft.App/managedEnvironments@2023-05-01' = {
  name: containerEnvName
  location: location
  properties: {
    appLogsConfiguration: {
      destination: 'log-analytics'
      logAnalyticsConfiguration: {
        customerId: logAnalytics.properties.customerId
        sharedKey: logAnalytics.listKeys().primarySharedKey
      }
    }
    zoneRedundant: false
    workloadProfiles: [
      {
        name: 'Consumption'
        workloadProfileType: 'Consumption'
      }
    ]
  }
  tags: {
    environment: environmentName
    application: appName
    component: 'shared'
  }
}

// =============================================================================
// OUTPUTS
// =============================================================================

@description('Managed Identity client ID')
output managedIdentityClientId string = managedIdentity.properties.clientId

@description('Managed Identity resource ID')
output managedIdentityId string = managedIdentity.id

@description('Log Analytics workspace ID')
output logAnalyticsWorkspaceId string = logAnalytics.id

@description('Container Apps Environment ID')
output containerEnvId string = containerEnv.id

@description('Container Registry login server')
output containerRegistryLoginServer string = '${containerRegistryName}.azurecr.io'

@description('Container Registry name')
output containerRegistryName string = containerRegistryName

@description('Resource group name')
output resourceGroupName string = resourceGroup().name
