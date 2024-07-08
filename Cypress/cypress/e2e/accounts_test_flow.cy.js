const webpageUrl = `${Cypress.env("webpageUrl")}`
const test_username = 'Cypress_testuser2';
const test_email = 'cypresstest2@test.com';
const test_password = 'R94M87ypJv';


describe('BudgetBuddy Accounts Flow Test', () => {

    it('User signup, login and logout', () => {

      cy.visit(webpageUrl)

      // Signup and login
      cy.get('#signupbtn').click()
      cy.get('#id_username').type(test_username)
      cy.get('#id_email').type(test_email)
      cy.get('#id_password1').type(test_password)
      cy.get('#id_password2').type(test_password)
      cy.get('.btn').click()
      cy.get('#id_username').type(test_username)
      cy.get('#id_password').type(test_password)
      cy.get('.btn').click()

      // Assertions
      //cy.get('.card-header').should('contain', `Welcome ${test_username}`);
      cy.get('.card-header')
      .invoke('text')
      .then((text) => {
        // Trim the text to remove leading and trailing whitespace
        const trimmedText = text.trim();
        expect(trimmedText).to.equal(`Welcome ${test_username}`);
      });
      cy.get('.list-group > :nth-child(1) > a').should('contain', `Categories`);
      cy.get('.list-group > :nth-child(2) > a').should('contain', `Budgets`);
      cy.get('.list-group > :nth-child(3) > a').should('contain', `Rulesets`);
      cy.get(':nth-child(4) > a').should('contain', `Reports`);
      cy.get(':nth-child(5) > a').should('contain', `Close account`);

      //Logout
      cy.get('#logoutbtn').click()
      // cy.get('.card-header').should('have.text', `Welcome`);

            // Assertions
      cy.get('.card-header')
      .invoke('text')
      .then((text) => {
        // Trim the text to remove leading and trailing whitespace
        const trimmedText = text.trim();
        expect(trimmedText).to.equal('Welcome');
      });

      cy.get('.list-group > :nth-child(1) > a').should('contain', `Categories`);
      cy.get('.list-group > :nth-child(2) > a').should('contain', `Budgets`);
      cy.get('.list-group > :nth-child(3) > a').should('contain', `Rulesets`);
      cy.get(':nth-child(4) > a').should('contain', `Reports`);
      })



      it('User login and delete account', () => {

        cy.login(test_username, test_password);
        cy.get('.card-header').should('contain', `Welcome ${test_username}`);
        cy.get('.list-group > :nth-child(1) > a').should('contain', `Categories`);
        cy.get('.list-group > :nth-child(2) > a').should('contain', `Budgets`);
        cy.get('.list-group > :nth-child(3) > a').should('contain', `Rulesets`);
        cy.get(':nth-child(4) > a').should('contain', `Reports`);
        cy.get(':nth-child(5) > a').as('closeAccountLink');
        cy.get('@closeAccountLink').should('contain', 'Close account');
        cy.get('@closeAccountLink').click();
        cy.get('.delete_user_username').should('contain', `${test_username}`);
        cy.get('.btn-outline-danger').click()
        cy.get('.card-header')
        .invoke('text')
        .then((text) => {
          // Trim the text to remove leading and trailing whitespace
          const trimmedText = text.trim();
          expect(trimmedText).to.equal('Welcome');
        });
        cy.get('.list-group > :nth-child(1) > a').should('contain', `Categories`);
        cy.get('.list-group > :nth-child(2) > a').should('contain', `Budgets`);
        cy.get('.list-group > :nth-child(3) > a').should('contain', `Rulesets`);
        cy.get(':nth-child(4) > a').should('contain', `Reports`);
        })

})
