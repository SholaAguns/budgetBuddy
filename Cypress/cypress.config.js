const { defineConfig } = require('cypress')

module.exports = defineConfig({
  env: {
        webpageUrl: 'http://localhost:8000',
  },
  e2e: {
    setupNodeEvents(on, config) {},
    supportFile: 'cypress/support/index.js',
  },
})
