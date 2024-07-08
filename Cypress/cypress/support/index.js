 require('./commands');
 import 'cypress-file-upload';

 Cypress.on('uncaught:exception', (err, runnable) => {
  // Return false to prevent Cypress from failing the test
  // if the error message includes 'Cannot read properties of null (reading 'getContext')'
  if (err.message.includes("Cannot read properties of null (reading 'getContext')")) {
    return false;
  }
});
