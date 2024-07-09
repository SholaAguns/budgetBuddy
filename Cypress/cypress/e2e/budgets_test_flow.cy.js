const webpageUrl = `${Cypress.env("webpageUrl")}`;
const existing_test_username = 'Cypress_testuser';
const existing_test_email = 'cypresstest@test.com';
const existing_test_password = 'x7rCW4nBdT';
const random = Math.floor(Math.random() * 100000);
const budgetName = 'Test Budget' + random;
const rulesetName = 'Test Ruleset' + random;

describe('BudgetBuddy Budgets Test Flow', () => {

        beforeEach(() => {
       // Replace with valid credentials for your application
       cy.login(existing_test_username, existing_test_password);
      });

      it('Create and delete a category', () => {

        cy.visit(webpageUrl)
        cy.get('.card-header').should('contain', `Welcome ${existing_test_username}`);
        cy.get('.list-group > :nth-child(1) > a').as('categoriesLink');
        cy.get('@categoriesLink').should('contain', 'Categories');
        cy.get('.list-group > :nth-child(2) > a').should('contain', `Budgets`);
        cy.get('.list-group > :nth-child(3) > a').should('contain', `Rulesets`);
        cy.get(':nth-child(4) > a').should('contain', `Reports`);
        cy.get(':nth-child(5) > a').as('closeAccountLink');
        cy.get('@closeAccountLink').should('contain', 'Close account');
        cy.get('@categoriesLink').click();

        // Categories Assertions
        cy.url().should('include', '/categories');
        cy.get('tbody')
        .find('tr')
        .should('have.length.gte', 12);

        //Add Category
        cy.get('.btn').click();
        cy.get('#id_title').type('Test Category');
        cy.get('.btn-outline-primary').click();

        //Add Category Assertion
        cy.get('tbody')
        .find('tr')
        .should('contain', 'Test Category');

        //Delete Category
        cy.contains('tbody tr', 'Test Category') // Find the row containing the text "Test Category"
       .find('a') // Find the <a> tag within that row
       .click(); // Click the <a> tag (which contains the delete icon)

       //Delete Category Assertion
       cy.contains('tbody tr', 'Test Category').should('not.exist');
        })

        it('Create a budget', () => {

          cy.createBudget('Test Budget')

          //Edit Budget name
          cy.contains('a', 'Edit Budget').click();
          cy.get('#id_name').clear().type(budgetName);
          cy.get('.btn-outline-primary').click();

          //Edit Budget name Assertion
          cy.get('#budgetname')
          .should('contain', budgetName);

            //Add Budget Categories
          cy.addBudgetCategory(budgetName, 'Food and Groceries', '500');
          cy.addBudgetCategory(budgetName, 'Entertainment', '100');
          cy.addBudgetCategory(budgetName, 'Takeout', '300');


          //Delete Budget Category
          cy.contains('tbody tr', 'Takeout')
         .find('a')
         .click();

         cy.deleteBudget(budgetName);

          })

          it('Create a ruleset', () => {

            cy.createRuleset('Test Ruleset')


            //Edit Ruleset name
            cy.contains('a', 'Edit Ruleset').click();
            cy.get('#id_name').clear().type(rulesetName);
            cy.get('.btn-outline-primary').click();

            //Edit Ruleset name Assertion
            cy.get('#rulesetname')
            .should('contain', rulesetName);

              //Add rules
            cy.addRule(rulesetName, 'Lidl', 'Food and Groceries');
            cy.addRule(rulesetName, 'Odeon', 'Entertainment');
            cy.addRule(rulesetName, 'The Grill', 'Takeout');


            //Delete rule
            cy.contains('tbody tr', 'The Grill')
           .find('a')
           .click();

           //Delete rule Assertion
           cy.contains('tbody tr', 'The Grill').should('not.exist');

           cy.deleteRuleset(rulesetName);


            })


})
