// =============================================================================
// Azure Bicep Template for Factory Agent - Azure Container Apps Deployment
// =============================================================================
// This Infrastructure as Code (IaC) template deploys the Factory Agent
// application to Azure Container Apps with all required resources.
//
// Resources Created:
// - Container Apps Environment (shared runtime for containers)
// - Container Registry (stores Docker images)
// - Log Analytics Workspace (monitoring and diagnostics)
// - Container App for Backend API (FastAPI)
// - Managed Identity (for secure Azure service access)
//
// Deployment:
//   az deployment group create \
//     --resource-group <rg-name> \
//     --template-file main.bicep \
//     --parameters main.bicepparam
//
// Cost Optimization:
// - Container Apps uses consumption plan (pay per use)
// - Container Registry uses Basic tier (low cost for demos)
// - Log Analytics with 30-day retention (minimal cost)
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

@description('Unique suffix for ACR name (6 chars, alphanumeric). Auto-generated from resource group.')
@maxLength(6)
param acrSuffix string = substring(uniqueString(resourceGroup().id), 0, 6)

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

@description('Allowed CORS origins (comma-separated)')
param allowedOrigins string = '*'

@description('Minimum number of container instances (0 for scale-to-zero)')
@minValue(0)
@maxValue(10)
param minReplicas int = 0

@description('Maximum number of container instances')
@minValue(1)
@maxValue(30)
param maxReplicas int = 5

@description('CPU cores per container instance')
@allowed([
  '0.25'
  '0.5'
  '0.75'
  '1.0'
  '1.25'
  '1.5'
  '1.75'
  '2.0'
])
param cpuCores string = '0.5'

@description('Memory per container instance (in GB)')
@allowed([
  '0.5'
  '1.0'
  '1.5'
  '2.0'
  '3.0'
  '4.0'
])
param memorySize string = '1.0'

// =============================================================================
// VARIABLES
// =============================================================================

var resourceNamePrefix = '${appName}-${environmentName}'
var containerRegistryName = replace('${appName}${acrSuffix}acr', '-', '') // ACR names: alphanumeric only, globally unique
var logAnalyticsName = '${resourceNamePrefix}-logs'
var containerEnvName = '${resourceNamePrefix}-env'
var backendAppName = '${resourceNamePrefix}-backend'
var managedIdentityName = '${resourceNamePrefix}-identity'

// Container image name (will be pushed to ACR by CI/CD)
var backendImageName = '${containerRegistryName}.azurecr.io/${appName}/backend:${imageTag}'

// =============================================================================
// RESOURCES
// =============================================================================

// -----------------------------------------------------------------------------
// User-Assigned Managed Identity
// -----------------------------------------------------------------------------
// Managed Identity provides secure authentication to Azure services without
// storing credentials. The Container App uses this identity to:
// - Pull images from Azure Container Registry
// - Access Azure Blob Storage (if enabled)
// - Write logs to Log Analytics
resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: managedIdentityName
  location: location
  tags: {
    environment: environmentName
    application: appName
  }
}

// -----------------------------------------------------------------------------
// Log Analytics Workspace
// -----------------------------------------------------------------------------
// Centralized logging and monitoring for all Container Apps in the environment.
// Stores container logs, application logs, and metrics for troubleshooting.
resource logAnalytics 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: logAnalyticsName
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'              // Pay-per-GB ingestion model
    }
    retentionInDays: 30              // Keep logs for 30 days (cost optimization)
    features: {
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
  tags: {
    environment: environmentName
    application: appName
  }
}

// -----------------------------------------------------------------------------
// Azure Container Registry (ACR)
// -----------------------------------------------------------------------------
// Private Docker registry for storing container images.
// CI/CD pipeline pushes built images here, Container Apps pulls from here.
resource containerRegistry 'Microsoft.ContainerRegistry/registries@2023-01-01-preview' = {
  name: containerRegistryName
  location: location
  sku: {
    name: 'Standard'                 // Standard tier (~$20/month, good balance)
  }
  properties: {
    adminUserEnabled: false          // Use Managed Identity instead (more secure)
    anonymousPullEnabled: false      // Require authentication to pull images
    publicNetworkAccess: 'Enabled'   // Allow access from internet (fine for demo)
    dataEndpointEnabled: false       // Not needed for Container Apps
    policies: {
      quarantinePolicy: {
        status: 'disabled'           // Quarantine disabled for simplicity
      }
      trustPolicy: {
        status: 'disabled'           // Content trust disabled for simplicity
      }
      retentionPolicy: {
        status: 'enabled'
        days: 30                     // Keep images for 30 days
      }
    }
  }
  tags: {
    environment: environmentName
    application: appName
  }
}

// Grant Managed Identity permission to pull images from ACR
// Role: AcrPull (7f951dda-4ed3-4680-a7ca-43fe172d538d)
resource acrPullRoleAssignment 'Microsoft.Authorization/roleAssignments@2022-04-01' = {
  name: guid(containerRegistry.id, managedIdentity.id, 'AcrPull')
  scope: containerRegistry
  properties: {
    roleDefinitionId: subscriptionResourceId('Microsoft.Authorization/roleDefinitions', '7f951dda-4ed3-4680-a7ca-43fe172d538d')
    principalId: managedIdentity.properties.principalId
    principalType: 'ServicePrincipal'
  }
}

// -----------------------------------------------------------------------------
// Container Apps Environment
// -----------------------------------------------------------------------------
// Shared runtime environment for all Container Apps.
// Provides networking, logging, and scaling infrastructure.
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
    zoneRedundant: false             // Single-zone for cost optimization
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
  }
}

// -----------------------------------------------------------------------------
// Container App - Backend API (FastAPI)
// -----------------------------------------------------------------------------
// The main backend API service running FastAPI with Uvicorn.
// Configured for auto-scaling, health checks, and secure secret management.
resource backendApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: backendAppName
  location: location
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${managedIdentity.id}': {}
    }
  }
  properties: {
    managedEnvironmentId: containerEnv.id
    workloadProfileName: 'Consumption'

    configuration: {
      // Ingress configuration (HTTP/HTTPS traffic)
      ingress: {
        external: true               // Accessible from internet
        targetPort: 8000             // Container listens on port 8000
        transport: 'http'            // HTTP protocol (HTTPS handled by Azure)
        allowInsecure: false         // Require HTTPS from clients
        traffic: [
          {
            latestRevision: true     // Route 100% traffic to latest revision
            weight: 100
          }
        ]
        corsPolicy: {
          allowedOrigins: split(allowedOrigins, ',')
          allowedMethods: ['GET', 'POST', 'OPTIONS']
          allowedHeaders: ['*']
          allowCredentials: true
        }
      }

      // Container registry configuration
      registries: [
        {
          server: containerRegistry.properties.loginServer
          identity: managedIdentity.id
        }
      ]

      // Secrets (stored securely, referenced by environment variables)
      secrets: [
        {
          name: 'azure-openai-key'
          value: azureOpenAiKey
        }
        {
          name: 'azure-storage-connection-string'
          value: azureStorageConnectionString
        }
      ]

      // Active revisions mode (single revision active at a time)
      activeRevisionsMode: 'Single'
    }

    template: {
      // Auto-scaling configuration
      scale: {
        minReplicas: minReplicas     // Scale to zero when idle (cost savings)
        maxReplicas: maxReplicas     // Max instances under load
        rules: [
          {
            name: 'http-scaling-rule'
            http: {
              metadata: {
                concurrentRequests: '10'  // Scale up when > 10 concurrent requests
              }
            }
          }
        ]
      }

      // Container configuration
      containers: [
        {
          name: 'backend'
          image: backendImageName
          resources: {
            cpu: json(cpuCores)      // CPU cores (0.5 = half a core)
            memory: '${memorySize}Gi' // Memory in GB
          }
          env: [
            {
              name: 'DEBUG'
              value: environmentName == 'dev' ? 'true' : 'false'
            }
            {
              name: 'LOG_LEVEL'
              value: environmentName == 'dev' ? 'debug' : 'info'
            }
            {
              name: 'STORAGE_MODE'
              value: storageMode
            }
            {
              name: 'AZURE_OPENAI_ENDPOINT'
              value: azureOpenAiEndpoint
            }
            {
              name: 'AZURE_OPENAI_KEY'
              secretRef: 'azure-openai-key'
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
              name: 'AZURE_STORAGE_CONNECTION_STRING'
              secretRef: 'azure-storage-connection-string'
            }
            {
              name: 'AZURE_STORAGE_CONTAINER_NAME'
              value: azureStorageContainerName
            }
            {
              name: 'ALLOWED_ORIGINS'
              value: allowedOrigins
            }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/health'
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 10
              periodSeconds: 30
              timeoutSeconds: 10
              successThreshold: 1
              failureThreshold: 3
            }
            {
              type: 'Readiness'
              httpGet: {
                path: '/health'
                port: 8000
                scheme: 'HTTP'
              }
              initialDelaySeconds: 5
              periodSeconds: 10
              timeoutSeconds: 5
              successThreshold: 1
              failureThreshold: 3
            }
          ]
        }
      ]
    }
  }
  tags: {
    environment: environmentName
    application: appName
  }
  dependsOn: [
    acrPullRoleAssignment
  ]
}

// =============================================================================
// OUTPUTS
// =============================================================================

@description('URL of the deployed backend API')
output backendUrl string = 'https://${backendApp.properties.configuration.ingress.fqdn}'

@description('Container Registry login server')
output containerRegistryLoginServer string = containerRegistry.properties.loginServer

@description('Container Registry name')
output containerRegistryName string = containerRegistry.name

@description('Managed Identity client ID')
output managedIdentityClientId string = managedIdentity.properties.clientId

@description('Managed Identity resource ID')
output managedIdentityId string = managedIdentity.id

@description('Log Analytics workspace ID')
output logAnalyticsWorkspaceId string = logAnalytics.id

@description('Container Apps Environment ID')
output containerEnvId string = containerEnv.id

@description('Backend app name')
output backendAppName string = backendApp.name

@description('Resource group name')
output resourceGroupName string = resourceGroup().name
