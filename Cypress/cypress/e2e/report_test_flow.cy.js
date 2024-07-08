const webpageUrl = `${Cypress.env("webpageUrl")}`;
const existing_test_username = 'Cypress_testuser';
const existing_test_email = 'cypresstest@test.com';
const existing_test_password = 'x7rCW4nBdT';
const random = Math.floor(Math.random() * 100000);
const budgetName = 'Test Budget' + random;
const rulesetName = 'Test Ruleset' + random;
const reportName = 'Test Report' + random;
const transactionFilename = "test_transaction_file.csv"
const startDate = '2024-06-01'
const endDate = '2025-06-01'

describe('BudgetBuddy Report Flow Test', () => {

        beforeEach(() => {
       // Replace with valid credentials for your application
       cy.login(existing_test_username, existing_test_password);
      });

      it('Create a report', () => {

        // Create budget
        cy.createBudget(budgetName);
        cy.addBudgetCategory(budgetName, 'Food and Groceries', '500');
        cy.addBudgetCategory(budgetName, 'Entertainment', '100');
        cy.addBudgetCategory(budgetName, 'Transportation', '300');
        cy.addBudgetCategory(budgetName, 'Sports and Exercise', '30');

        // Create ruleset
        cy.createRuleset(rulesetName);
        cy.addRule(rulesetName, 'Lidl', 'Food and Groceries');
        cy.addRule(rulesetName, 'Odeon', 'Entertainment');
        cy.addRule(rulesetName, 'TFL', 'Transportation');
        cy.addRule(rulesetName, 'Footy', 'Sports and Exercise');

        cy.createReport(reportName, startDate, endDate, transactionFilename);

        cy.get('#add_ruleset_btn').click();
        cy.get('#id_ruleset').select(rulesetName);
        cy.get('.btn-outline-primary').click();


        cy.get('#add_budget_btn').click();
        cy.get('#id_budget').select(budgetName);
        cy.get('.btn-outline-primary').click();

        cy.get('#transactions_section_caret').click();
        cy.contains('a', 'Import Transactions').click();

        //Assertions
        cy.get('.expenses_section_heading')
        .should('contain', 'Expenses');

        cy.get('.earnings_section_heading')
        .should('contain', 'Earnings');

        cy.get('.budvact_section')
        .should('contain', 'Budget  vs Actual');




        })

})
