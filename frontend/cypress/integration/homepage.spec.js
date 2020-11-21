/// <reference types="cypress" />

context('Homepage', () => {
  beforeEach(() => {
    cy.visit('http://localhost:8080')
  })

  it('should have the title', () => {
    // TODO: have better titles
    cy.title().should('equal', 'Course Data Explorer')
  })

  it('should show campus cards', () => {
    cy.get('.card.campus')
      .should('have.length.greaterThan', 1)
  })

  it('should navigate to a campus on click', () => {
    cy.get('.card.campus')
      .first()
      .click()

    cy.location('pathname')
      .should('match', /\/explore\/([A-Z\-]*)/)
  })
})
