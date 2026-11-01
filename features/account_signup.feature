Feature: Account signup
  Students can create an account to participate in Campus Connect.

  Scenario: A student signs up with valid details
    Given I open the account creation page
    When I submit these account details:
      | username | email                  | password1             | password2             |
      | newuser  | newuser@example.com    | Campus-connect-2026!  | Campus-connect-2026!  |
    Then I am redirected to the home page
    And an account exists for "newuser"
    And I am logged in as "newuser"

  Scenario: A student cannot register with an existing username
    Given a registered user "existinguser" exists
    And I open the account creation page
    When I submit these account details:
      | username     | email                      | password1            | password2            |
      | existinguser | another@example.com        | Campus-connect-2026! | Campus-connect-2026! |
    Then signup is rejected and the existing account is unchanged
