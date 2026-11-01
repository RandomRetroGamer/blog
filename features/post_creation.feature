Feature: Post creation
  Students must be signed in to publish posts.

  Scenario: A signed-in student publishes a post
    Given a registered user "postauthor" exists
    And I am logged in as "postauthor"
    When I publish a post titled "Campus meetup" with body "Meet in the library."
    Then I am redirected to the home page
    And the post "Campus meetup" appears on the home page
    And the post was written by "postauthor"

  Scenario: An anonymous visitor cannot publish a post
    When I publish a post titled "Anonymous post" with body "This should not be published."
    Then I am redirected to the login page
    And no post titled "Anonymous post" exists
