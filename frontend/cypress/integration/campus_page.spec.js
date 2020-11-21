/// <reference types="cypress" />

context('Campus Page', () => {
  beforeEach(() => {
    cy.visit('http://localhost:8080/explore/fh')
  })

  // TODO: add custom titles
  // it('should have a custom window title', () => {
  //   cy.title().should('equal', 'Foothill College | Course Data Explorer')
  // })

  it('should have a title on the page', () => {
    cy.get('.root h1')
      .should('have.length', 1)
  })

  it('should show department cards', () => {
    cy.get('.card.dept')
      .should('have.length.greaterThan', 1)
  })

  it('should navigate to a department on click', () => {
    cy.get('.card.dept')
      .first()
      .click()

    cy.location('pathname')
      .should('match', /\/explore\/fh\/dept\/([A-Z\-]*)/)
  })

  it('should show a filter input', () => {
    cy.get('.title-container input')
      .should('have.length', 1)
  })

  it('should filter departments', () => {
    cy.get('.title-container input')
      .type('math')
      .should('have.value', 'math')

    cy.get('.card.dept')
      .first()
      .should('exist')
      .contains('math', { matchCase: false })
  })

  it('should show a term picker', () => {
    cy.get('.title-container .select-wrapper select')
      .should('have.length', 1)
  })

  it('should have at least one option in the term picker', () => {
    cy.get('.title-container .select-wrapper select option')
      .should('have.length.gte', 1)
  })

  describe('Switching the Term', () => {
    beforeEach(() => {
      cy.server()
      cy.route('GET', '**/fh/depts?year=2020&quarter=fall').as('depts')

      cy.get('.title-container .select-wrapper select')
        .should('have.length.gte', 1)
        .select('Fall 2020')
        .should('have.value', 'fall-2020')
    })

    it('should update the URL', () => {
      cy.location('search')
        .should('include', 'year=2020')
        .should('include', 'term=fall')
    })

    it('should refetch data', () => {
      cy.wait('@depts')
        .should('have.property', 'status', 200)
    })
  })
})
