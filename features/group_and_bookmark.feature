Feature: Groups and bookmarks
  Students can participate in groups and save posts for later.

  Scenario: A signed-in student joins a group
    Given a group "Computer Science" with slug "computer-science" exists
    And a registered user "groupmember" exists
    And I am logged in as "groupmember"
    When I join the group "computer-science"
    Then I am a member of the group "computer-science"

  Scenario: A group member publishes a post
    Given a group "Engineering" with slug "engineering" exists
    And a registered user "groupauthor" exists
    And I am logged in as "groupauthor"
    And the user is already a member of the group "engineering"
    When I publish a group post titled "Design workshop" with body "Meet in the lab." in "engineering"
    Then the post "Design workshop" exists in the group "engineering"
    And the post was written by "groupauthor"

  Scenario: A non-member cannot publish a group post
    Given a group "Biology" with slug "biology" exists
    And a registered user "visitor" exists
    And I am logged in as "visitor"
    When I publish a group post titled "Restricted post" with body "I have not joined." in "biology"
    Then no post titled "Restricted post" exists

  Scenario: A student removes a post from bookmarks
    Given a registered user "bookmarkuser" exists
    And I am logged in as "bookmarkuser"
    And a post titled "Study notes" by "bookmarkuser" exists
    When I bookmark the post titled "Study notes"
    Then the post "Study notes" appears in my bookmarks
    When I bookmark the post titled "Study notes"
    Then the post "Study notes" is not in my bookmarks
