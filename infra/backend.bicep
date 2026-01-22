// =============================================================================
// Backend Container App for Factory Agent
// =============================================================================
// This Bicep template deploys ONLY the backend FastAPI Container App.
// It references shared resources created by shared.bicep.
//
// Prerequisites:
// - Deploy shared.bicep first to create Container Environment, Log Analytics, etc.
//
// Deployment:
//   az deployment group create \
//     --resource-group <rg-name> \
//     --template-file backend.bicep \
//     --parameters imageTag="1a6e6f..." azureAiKey="..." azureAiEndpoint="..."
// =============================================================================

// =============================================================================
// PARAMETERS
// =============================================================================

@description('Name of the application')
param appName string = 'factory-agent'

@description('Azure region for resources')
param location string = resourceGroup().location

@description('Environment name (dev, staging, prod)')
@allowed(['dev', 'staging', 'prod'])
param environmentName string = 'dev'

@description('Container image tag (commit SHA or semantic version)')
param imageTag string = 'latest'

@description('Existing Azure Container Registry name')
param containerRegistryName string = 'factoryagent4u4zqkacr'

@description('Azure AI Foundry endpoint URL')
@secure()
param azureAiEndpoint string

@description('Azure AI Foundry API key')
@secure()
param azureAiKey string

@description('Azure AI model deployment name')
param azureAiDeployment string = 'gpt-4o'

@description('Azure AI API version')
param azureAiApiVersion string = '2024-08-01-preview'

@description('Storage mode: local or blob')
@allowed(['local', 'blob'])
param storageMode string = 'blob'

@description('Azure Storage connection string (required if storageMode=blob)')
@secure()
param azureStorageConnectionString string = ''

@description('Azure Storage container name')
param azureStorageContainerName string = 'factory-data'

@description('Allowed CORS origins (comma-separated)')
param allowedOrigins string = ''

@description('Static Web App hostname for CORS (e.g., xxx.azurestaticapps.net)')
param staticWebAppHostname string = ''

@description('Minimum replicas')
@minValue(0)
@maxValue(10)
param minReplicas int = 0

@description('Maximum replicas')
@minValue(1)
@maxValue(30)
param maxReplicas int = 5

@description('CPU cores per container')
@allowed(['0.25', '0.5', '0.75', '1.0', '1.25', '1.5', '1.75', '2.0'])
param cpuCores string = '0.5'

@description('Memory per container (GB)')
@allowed(['0.5', '1.0', '1.5', '2.0', '3.0', '4.0'])
param memorySize string = '1.0'

// =============================================================================
// VARIABLES
// =============================================================================

var resourceNamePrefix = '${appName}-${environmentName}'
var backendAppName = '${resourceNamePrefix}-backend'
var containerEnvName = '${resourceNamePrefix}-env'
var managedIdentityName = '${resourceNamePrefix}-identity'

var backendImageName = '${containerRegistryName}.azurecr.io/${appName}/backend:${imageTag}'

// Build CORS origins array: user-provided origins + Static Web App origin (if provided)
var userOrigins = allowedOrigins != '' ? split(allowedOrigins, ',') : []
var swaOrigin = staticWebAppHostname != '' ? ['https://${staticWebAppHostname}'] : []
var allCorsOrigins = concat(userOrigins, swaOrigin)

// =============================================================================
// EXISTING RESOURCES (from shared.bicep)
// =============================================================================

resource containerEnv 'Microsoft.App/managedEnvironments@2023-05-01' existing = {
  name: containerEnvName
}

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: managedIdentityName
}

// =============================================================================
// BACKEND CONTAINER APP
// =============================================================================

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
      ingress: {
        external: true
        targetPort: 8000
        transport: 'http'
        allowInsecure: false
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
        corsPolicy: {
          // Allow configured origins, or '*' if none specified
          allowedOrigins: length(allCorsOrigins) > 0 ? allCorsOrigins : ['*']
          allowedMethods: ['GET', 'POST', 'OPTIONS']
          allowedHeaders: ['*']
          allowCredentials: true
        }
      }

      registries: [
        {
          server: '${containerRegistryName}.azurecr.io'
          identity: managedIdentity.id
        }
      ]

      secrets: concat([
        {
          name: 'azure-ai-key'
          value: azureAiKey
        }
      ], storageMode == 'blob' ? [
        {
          name: 'azure-storage-connection-string'
          value: azureStorageConnectionString
        }
      ] : [])

      activeRevisionsMode: 'Single'
    }

    template: {
      scale: {
        minReplicas: minReplicas
        maxReplicas: maxReplicas
        rules: [
          {
            name: 'http-scaling-rule'
            http: {
              metadata: {
                concurrentRequests: '10'
              }
            }
          }
        ]
      }

      containers: [
        {
          name: 'backend'
          image: backendImageName
          resources: {
            cpu: json(cpuCores)
            memory: '${memorySize}Gi'
          }
          env: concat([
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
              name: 'AZURE_ENDPOINT'
              value: azureAiEndpoint
            }
            {
              name: 'AZURE_API_KEY'
              secretRef: 'azure-ai-key'
            }
            {
              name: 'AZURE_DEPLOYMENT_NAME'
              value: azureAiDeployment
            }
            {
              name: 'AZURE_API_VERSION'
              value: azureAiApiVersion
            }
          ], storageMode == 'blob' ? [
            {
              name: 'AZURE_STORAGE_CONNECTION_STRING'
              secretRef: 'azure-storage-connection-string'
            }
            {
              name: 'AZURE_STORAGE_CONTAINER_NAME'
              value: azureStorageContainerName
            }
          ] : [], [
            {
              name: 'ALLOWED_ORIGINS'
              value: allowedOrigins
            }
          ])
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
    component: 'backend'
  }
}

// =============================================================================
// OUTPUTS
// =============================================================================

@description('URL of the deployed backend API')
output backendUrl string = 'https://${backendApp.properties.configuration.ingress.fqdn}'

@description('Backend app name')
output backendAppName string = backendApp.name

@description('Backend image deployed')
output backendImage string = backendImageName
