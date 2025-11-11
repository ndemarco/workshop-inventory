/**
 * Application configuration from environment variables
 */

export const config = {
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || '/api',
  appName: import.meta.env.VITE_APP_NAME || 'Homelab Inventory System',
  appDescription: import.meta.env.VITE_APP_DESCRIPTION || 'A comprehensive inventory management system',
  
  // Feature flags
  features: {
    qrScanning: true,
    duplicateDetection: true,
    specExtraction: true,
    locationSuggestions: true,
  },
  
  // Pagination
  pagination: {
    itemsPerPage: 20,
    maxResults: 100,
  },
  
  // Timeouts
  timeouts: {
    apiTimeout: 10000, // 10 seconds
    debounceDelay: 300, // 300ms
  },
};

export default config;
