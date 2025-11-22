// =============================================================================
// Frontend Container App for Factory Agent
// =============================================================================
// This Bicep template deploys ONLY the frontend React Container App.
// It references shared resources created by shared.bicep and backend.bicep.
//
// Prerequisites:
// - Deploy shared.bicep first to create Container Environment
// - Deploy backend.bicep to get backend URL
//
// Deployment:
//   az deployment group create \
//     --resource-group <rg-name> \
//     --template-file frontend.bicep \
//     --parameters imageTag="1a6e6f..."
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

@description('Minimum replicas')
@minValue(0)
@maxValue(10)
param minReplicas int = 0

@description('Maximum replicas')
@minValue(1)
@maxValue(30)
param maxReplicas int = 5

// =============================================================================
// VARIABLES
// =============================================================================

var resourceNamePrefix = '${appName}-${environmentName}'
var frontendAppName = '${resourceNamePrefix}-frontend'
var backendAppName = '${resourceNamePrefix}-backend'
var containerEnvName = '${resourceNamePrefix}-env'
var managedIdentityName = '${resourceNamePrefix}-identity'

var frontendImageName = '${containerRegistryName}.azurecr.io/${appName}/frontend:${imageTag}'

// =============================================================================
// EXISTING RESOURCES
// =============================================================================

resource containerEnv 'Microsoft.App/managedEnvironments@2023-05-01' existing = {
  name: containerEnvName
}

resource managedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' existing = {
  name: managedIdentityName
}

resource backendApp 'Microsoft.App/containerApps@2023-05-01' existing = {
  name: backendAppName
}

// =============================================================================
// FRONTEND CONTAINER APP
// =============================================================================

resource frontendApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: frontendAppName
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
        targetPort: 80
        transport: 'http'
        allowInsecure: false
        traffic: [
          {
            latestRevision: true
            weight: 100
          }
        ]
      }

      registries: [
        {
          server: '${containerRegistryName}.azurecr.io'
          identity: managedIdentity.id
        }
      ]

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
                concurrentRequests: '20'
              }
            }
          }
        ]
      }

      containers: [
        {
          name: 'frontend'
          image: frontendImageName
          resources: {
            cpu: json('0.25')
            memory: '0.5Gi'
          }
          env: [
            {
              name: 'NODE_ENV'
              value: 'production'
            }
            {
              name: 'VITE_API_BASE_URL'
              value: 'https://${backendApp.properties.configuration.ingress.fqdn}'
            }
            {
              name: 'APP_VERSION'
              value: imageTag
            }
          ]
          probes: [
            {
              type: 'Liveness'
              httpGet: {
                path: '/health'
                port: 80
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
                port: 80
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
    component: 'frontend'
  }
}

// =============================================================================
// OUTPUTS
// =============================================================================

@description('URL of the deployed frontend application')
output frontendUrl string = 'https://${frontendApp.properties.configuration.ingress.fqdn}'

@description('Frontend app name')
output frontendAppName string = frontendApp.name

@description('Frontend image deployed')
output frontendImage string = frontendImageName
