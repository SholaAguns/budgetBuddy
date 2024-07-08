const webpageUrl = Cypress.env("webpageUrl");

Cypress.Commands.add('login', (username, password) => {

    cy.visit(`${webpageUrl}/accounts/login/`);
    cy.get('#id_username').type(username);
    cy.get('#id_password').type(password);
    cy.get('.btn').click();
    //Assertions
    cy.get('.card-header').should('contain', `Welcome ${username}`);
    cy.get('.list-group > :nth-child(1) > a').should('contain', `Categories`);
    cy.get('.list-group > :nth-child(2) > a').should('contain', `Budgets`);
    cy.get('.list-group > :nth-child(3) > a').should('contain', `Rulesets`);
    cy.get(':nth-child(4) > a').should('contain', `Reports`);
    cy.get(':nth-child(5) > a').as('closeAccountLink');
    cy.get('@closeAccountLink').should('contain', 'Close account');
});


Cypress.Commands.add('createBudget', (budgetName) => {
  cy.visit(webpageUrl)
  cy.get('.list-group > :nth-child(1) > a').as('categoriesLink');
  cy.get('@categoriesLink').should('contain', 'Categories');
  cy.get('.list-group > :nth-child(2) > a').as('budgetsLink');
  cy.get('@budgetsLink').should('contain', 'Budgets');
  cy.get('.list-group > :nth-child(3) > a').should('contain', `Rulesets`);
  cy.get(':nth-child(4) > a').should('contain', `Reports`);
  cy.get(':nth-child(5) > a').as('closeAccountLink');
  cy.get('@closeAccountLink').should('contain', 'Close account');
  cy.get('@budgetsLink').click();


  //Add Budget
  cy.get('.btn').click();
  cy.get('#id_name').type(budgetName);
  cy.get('.btn-outline-primary').click();

  //Add Budget Assertion
  cy.get('#budgetname')
  .should('contain', budgetName);
});

Cypress.Commands.add('deleteBudget', (budgetName) => {

  cy.visit(`${webpageUrl}/budgets/`);

  cy.contains('.budget_name', budgetName)
  .find('a')
  .click();

  //Delete Budget
  cy.contains('a', 'Delete Budget').click();
  cy.get('.btn-outline-danger').click();

  //Delete Budget Assertion
  cy.contains('tbody tr', budgetName).should('not.exist');
});

Cypress.Commands.add('addBudgetCategory', (budgetName, category, limit) => {

  cy.visit(`${webpageUrl}/budgets/`);

  cy.contains('.budget_name', budgetName)
  .find('a')
  .click();


  //Add Budget Category
  cy.contains('a', 'Add Category').click();
  cy.get('#id_category').select(category);
  cy.get('#id_limit').type(limit)
  cy.get('.btn-outline-primary').click();

  //Add Budget Category Assertion
  cy.get('tbody')
  .find('tr')
  .should('contain', category)
  .should('contain', limit);
});

Cypress.Commands.add('createRuleset', (rulesetName) => {
    cy.visit(webpageUrl)
    cy.get('.list-group > :nth-child(1) > a').as('categoriesLink');
    cy.get('@categoriesLink').should('contain', 'Categories');
    cy.get('.list-group > :nth-child(2) > a').as('budgetsLink');
    cy.get('@budgetsLink').should('contain', 'Budgets');
    cy.get('.list-group > :nth-child(3) > a').as('rulesetsLink');
    cy.get('@rulesetsLink').should('contain', 'Rulesets');
    cy.get(':nth-child(4) > a').should('contain', `Reports`);
    cy.get(':nth-child(5) > a').as('closeAccountLink');
    cy.get('@closeAccountLink').should('contain', 'Close account');
    cy.get('@rulesetsLink').click();


    //Add Ruleset
    cy.get('.btn').click();
    cy.get('#id_name').type(rulesetName);
    cy.get('.btn-outline-primary').click();

    //Add Ruleset Assertion
    cy.get('#rulesetname')
    .should('contain', rulesetName);
});

Cypress.Commands.add('addRule', (rulesetName, keyword, category) => {

  cy.visit(`${webpageUrl}/budgets/rulesets`);

  cy.contains('.ruleset_name', rulesetName)
  .find('a')
  .click();

  //Add rule
  cy.contains('a', 'Add Rule').click();
  cy.get('#id_category').select(category);
  cy.get('#id_keyword').type(keyword)
  cy.get('.btn-outline-primary').click();

  //Add rule Assertion
  cy.get('tbody')
  .find('tr')
  .should('contain', keyword)
  .should('contain', category);

});

Cypress.Commands.add('deleteRuleset', (rulesetName) => {

  cy.visit(`${webpageUrl}/budgets/rulesets`);

  cy.contains('.ruleset_name', rulesetName)
  .find('a')
  .click();

  //Delete Ruleset
  cy.contains('a', 'Delete Ruleset').click();
  cy.get('.btn-outline-danger').click();

  //Delete Ruleset Assertion
  cy.contains('tbody tr', rulesetName).should('not.exist');
});

Cypress.Commands.add('createReport', (reportName, startDate, endDate, fileName) => {
  cy.visit(webpageUrl)
  cy.get('.list-group > :nth-child(1) > a').as('categoriesLink');
  cy.get('@categoriesLink').should('contain', 'Categories');
  cy.get('.list-group > :nth-child(2) > a').as('budgetsLink');
  cy.get('@budgetsLink').should('contain', 'Budgets');
  cy.get('.list-group > :nth-child(3) > a').should('contain', `Rulesets`);
  cy.get('.list-group > :nth-child(4) > a').as('reportsLink');
  cy.get('@reportsLink').should('contain', 'Reports');
  cy.get(':nth-child(5) > a').as('closeAccountLink');
  cy.get('@closeAccountLink').should('contain', 'Close account');
  cy.get('@reportsLink').click();


  //Add Report
  cy.get('.btn').click();
  cy.get('#id_name').type(reportName);
  cy.get('#id_start_date').type(startDate);
  cy.get('#id_end_date').type(endDate);
  cy.get('#id_transaction_sheet').attachFile(fileName);

   // Submit the form
   cy.get('form.budget-form').submit();

  //Add Report Assertion
  cy.get('.report_heading')
  .should('contain', reportName);
});
