// =============================================================================
// Static Web App for Factory Agent Frontend
// =============================================================================
// This Bicep template deploys an Azure Static Web App for the React frontend.
// Replaces the frontend Container App with a free-tier static hosting solution.
//
// Features:
// - Free tier ($0/month)
// - Global CDN included
// - Automatic HTTPS
// - SPA routing via staticwebapp.config.json
//
// Prerequisites:
// - Backend Container App must be deployed (for CORS configuration)
// - GitHub repository connected for deployment
//
// Deployment:
//   az deployment group create \
//     --resource-group <rg-name> \
//     --template-file staticwebapp.bicep \
//     --parameters environmentName=dev
//
// Post-Deployment:
//   1. Get deployment token: az staticwebapp secrets list --name <name> --query "properties.apiKey"
//   2. Add token to GitHub secrets as AZURE_STATIC_WEB_APPS_API_TOKEN
// =============================================================================

// =============================================================================
// PARAMETERS
// =============================================================================

@description('Name of the application')
param appName string = 'factory-agent'

@description('Azure region for the Static Web App')
@allowed([
  'centralus'
  'eastus2'
  'eastasia'
  'westeurope'
  'westus2'
])
param location string = 'eastus2'

@description('Environment name (dev, staging, prod)')
@allowed(['dev', 'staging', 'prod'])
param environmentName string = 'dev'

@description('GitHub repository URL (e.g., https://github.com/owner/repo)')
param repositoryUrl string = ''

@description('GitHub branch for deployments')
param branch string = 'main'

@description('Static Web App SKU')
@allowed(['Free', 'Standard'])
param sku string = 'Free'

// =============================================================================
// VARIABLES
// =============================================================================

var resourceNamePrefix = '${appName}-${environmentName}'
var staticWebAppName = '${resourceNamePrefix}-frontend-swa'

// =============================================================================
// RESOURCES
// =============================================================================

// -----------------------------------------------------------------------------
// Static Web App
// -----------------------------------------------------------------------------
// Hosts the React frontend with global CDN, automatic HTTPS, and SPA routing.
// Free tier includes 100GB bandwidth/month (sufficient for demo/dev use).
resource staticWebApp 'Microsoft.Web/staticSites@2022-09-01' = {
  name: staticWebAppName
  location: location
  sku: {
    name: sku
    tier: sku
  }
  properties: {
    // Repository configuration (optional - can be linked later via GitHub Actions)
    repositoryUrl: repositoryUrl != '' ? repositoryUrl : null
    branch: repositoryUrl != '' ? branch : null

    // Build configuration
    buildProperties: {
      appLocation: 'frontend'           // React app source location
      outputLocation: 'dist'            // Vite build output directory
      skipGithubActionWorkflowGeneration: true  // We manage our own workflow
    }

    // Staging environments (disabled for Free tier)
    stagingEnvironmentPolicy: sku == 'Free' ? 'Disabled' : 'Enabled'
  }
  tags: {
    environment: environmentName
    application: appName
    component: 'frontend'
    'migration-from': 'container-app'
  }
}

// =============================================================================
// OUTPUTS
// =============================================================================

@description('Static Web App default hostname')
output defaultHostname string = staticWebApp.properties.defaultHostname

@description('Static Web App URL')
output siteUrl string = 'https://${staticWebApp.properties.defaultHostname}'

@description('Static Web App resource ID')
output resourceId string = staticWebApp.id

@description('Static Web App name')
output staticWebAppName string = staticWebApp.name

@description('CORS origin to add to backend (use this value for ALLOWED_ORIGINS)')
output corsOrigin string = 'https://${staticWebApp.properties.defaultHostname}'
