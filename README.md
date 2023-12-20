# Family Movie Night

#### Video Demo: <https://www.youtube.com/watch?v=0gWJqlGqATA>

## Description:
Welcome to the Pride's Ultimate Movie Night Experience!

Introducing my innovative project, Family Movie Night, where I tried to bring the family together to choose the perfect movie for the evening based on everyone's preferences. Here's how it works:

### Register and Log In/Out:

* Get started by creating an account to make your movie nights even more personalized.

* Log in and Logout seamlessly to ensure your preferences are saved for future reference. Log out located in the dropdown menu in user's profile.

### Vote for Your Favorite Movie:

* Enter the movie name you're rooting for.

* Provide the movie's poster URL (both fields are mandatory).

* Click the "Vote" button to cast your ballot.

### Interactive Voting Experience:

* Your family members can see your movie choice poster, and it will be marked as your vote on your dedicated page.

* Feel free to change your vote at any time based on your evolving preferences (assuming movie hasn’t been drawn yet).

### Draw the Winner:

* Once all family members have cast their votes, someone can hit the "Draw" button.

* Discover the winning movie for the day and get ready for an exciting movie night!

### Daily Movie Selections:

* All movie selections are visible only for the calendar day.

* If you forget to click the draw button from the previous day, your selections will vanish, ensuring a fresh start for each movie night.

**Join the Pride and make your family movie nights unforgettable!**

  

### Database
All system data is stored in DB that will be created on first DB access attempt.

DB includes next tables:
* users (id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR (15) NOT NULL, hash VARCHAR (20) NOT NULL);

* votes (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, movie_name TEXT NOT NULL, timestamp TEXT NOT NULL, status INTEGER NOT NULL, poster_url TEXT NOT NULL);

### Project Structure:
app.py - contains the main project code
helpers.py - contains several helper functions
requirements.txt - contains the list of project dependencies
styles.css - contains all css styles
about.html - contains info about author
apology.html - contains html code for error screen
homepage.html - the main page of the project where user can vote for the movie, change the vote, draw the movie
layout.html - basic template for other website pages
login.html - contains login functionality
register.html - contains register functionality

### Setup instructions
Install dependencies from requirements.txt
**pip install -r requirements.txt**