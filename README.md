# utrgv-3340-fall2026-group-project-1-group-8
Group : hot rod

Project goal :
we created a user based web-app where the users can create a post based on their major and ask a question. In other words it is a student based forum or "reddit"

# setting up our project
clone the repo
> git clone : https://github.com/UTRGV-3340/utrgv-3340-fall2026-group-project-1-group-8.git

create a python virtual enviroment
> python -m venv myenv

activating python enviroment 
> python3 -m venv myenv

install python lib
> pip install -r requirements.txt

starting the django server set up 
> python3 manage.py makemigrations
> && python3 manage.py migrate

these are incase if the migrate folder doesn't exist!

the build.sh and start.sh is for render ONLY! i intended on using them for
live demos in the class however render needed them to actually set up the project
for us we are going to stick with the basic start up

> python3 manage.py runserver

and that is it! you can try some of the test we have made / behave features for 
your self

with the virtual enviroment still active use these commands
> python3 manage.py test && python3 manage.py behave


# Understanding our Workflow

Since the beginning of the work we had it in back of our minds
to create test along with each feature. Some coverage is 
more than other and setting priorties

-> add feature -> add test -> test the entire branch -> (if works then we push to main)

# How much test are built into this website?

### Test summary

| Test class | Area | Tests |
|---|---|---|
| `EventTests` | Events | 8 |
| `PasswordResetTests` | Authentication: password reset | 4 |
| `SignupTests` | Authentication: signup | 1 |
| `PostAndCommentTests` | Posts and comments | 4 |
| `ModerationTests` | Staff moderation and security | 6 |
| `GroupTests` | Groups | 7 |
| `BookmarkTests` | Bookmarks | 5 |
| `EnsureAdminUserTests` | Admin management command | 4 |
| **Total** | | **39** |

### Coverage by feature area

| Feature area | What's covered | Tests |
|---|---|---|
| **Events** | Staff creation, end-before-start validation, public list/detail pages, joining, posting and commenting while active, closing by admin, auto-close at end time | 8 |
| **Authentication: signup** | Valid signup, auto-login, redirect home | 1 |
| **Authentication: password reset** | Reset link on login page, email sent with configured base URL, password updates, invalid token handling | 4 |
| **Posts** | Creation by logged-in users, anonymous users redirected to login | 2 |
| **Comments** | Creation by logged-in users, anonymous users redirected to login | 2 |
| **Moderation** | Staff can remove posts (cascading to comments) and comments, non-staff blocked, POST-only enforcement, CSRF failure recovery, feed `no-store` caching | 6 |
| **Groups** | Starter groups, list page, join/leave, anonymous blocked, member vs. non-member posting, post isolation between groups | 7 |
| **Bookmarks** | Toggle on/off, privacy between users, per-user feed state, anonymous blocked, POST-only, open-redirect protection | 5 |
| **Admin management command** | Creates superuser from environment variables, leaves existing admin unchanged, refuses to promote regular users, requires password variable | 4 |



along with the test we have # feature test along with all passing 

## Features

- **Student accounts:** Sign up, log in, log out, and reset passwords.
- **Community posts:** Signed-in users can publish posts and comment on discussions.
- **Groups:** Browse groups, join or leave them, and publish posts as a group member.
- **Bookmarks:** Save posts to a personal bookmarks page and remove them when they are no longer needed.
- **Campus events:** Browse events, join upcoming events, and take part in event discussions while they are active.
- **Moderation:** Staff can pin or remove posts and remove comments.
- **About page:** Read information about the Campus Connect community.

# project breakdown

The project is one of the largest projects i (randy coronado) have worked on so far but to say the least it was a learning experince. 

### **setting up login accounts for blog**
the first things we did was did was setting up Django in python, and starting the login process. The main part of this wesbite is having students posting under their usernames / comments / joining events / etc

### **setting up basic posting and commenting**
The second step is setting up posting and comments on the main home page, this was quiet easy to set up due to django's built in functions 

### **adding basic groups / admin actions**
The whole point of this project is students being able to connecting to other students in the same majors. We created groups that other people can join and post under

The admin was simple use, deleteing post / pinning post to the top of the page

we will go deeper into admin's actions later

### **Adding design**
for sprint 2 the project was quiet messy so we added some boxes for the users to be able to see what is going on in the demo

This was later overhauled for sprint 3 based on user feedback

# Understanding admins
Admins keep the peace in this website if you will

Actions they can do:
- create groups
- create events
- pinning post
- booking marking post
- delete users
- delete post
- delete comments

# undersanding users
for the users to use the website the first thing is creating an account. they have to use a proper email for starters.

Actions they can do:
- join a group
- bookmarking post
- exploring groups
- create a post
- create a comment
- join events

