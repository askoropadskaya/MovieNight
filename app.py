from datetime import date, timedelta
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

from helpers import apology, login_required

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db_con = sqlite3.connect("movienight.db", check_same_thread=False)
create_users_table = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR (15) NOT NULL, hash VARCHAR (20) NOT NULL);"
create_votes_table = "CREATE TABLE IF NOT EXISTS votes (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, movie_name TEXT NOT NULL, timestamp TEXT NOT NULL);"
db_con.cursor().execute(create_users_table)
db_con.cursor().execute(create_votes_table)


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def hello():
    today = date.today()
    vote = db_con.cursor().execute(
            "SELECT * FROM votes WHERE user_id = ? AND timestamp = ?", (session["user_id"], today)
        ).fetchone()
    print(f"vote={vote}")
    voted = (vote != None)

    all_votes = db_con.cursor().execute(
        "SELECT * FROM votes WHERE timestamp = ?", (today,)
    ).fetchall()
    print(f"all today's votes: {all_votes}")

    if request.method == "GET":
        return render_template("homepage.html", voted=voted, vote=vote, today=today, all_votes=all_votes)
        
    if request.method == "POST":
        if not request.form.get("moviename"):
            return apology("must provide movie name", 400)
        
        # db_con.cursor().execute(
        #     "INSERT OR IGNORE INTO votes (user_id, movie_name, timestamp) VALUES (?, ?, ?)", (session["user_id"],request.form.get("moviename"),  today)
        # ).fetchone()

        # db_con.cursor().execute(
        #     "UPDATE votes SET movie_name = ? WHERE user_id=? and timestamp=?", (request.form.get("moviename"), session["user_id"], today)
        # )
        if voted:
            db_con.cursor().execute(
                "UPDATE votes set movie_name = ? WHERE id = ?", (request.form.get("moviename"), vote[0])
            )
            db_con.commit()
        else:
            db_con.cursor().execute(
                "INSERT into votes (user_id, movie_name, timestamp) VALUES(?,?,?)", (session["user_id"],request.form.get("moviename"),  today)
            )
            db_con.commit()
        return redirect("/")    


@app.route("/draw", methods=["POST"])
@login_required
def draw():
    return apology("draw test")

# @app.route("/apology")
# def testApology():
#     return apology("Test error message")

# @app.route('/about/')
# def about():
#     return '<h3>This is a Flask web application.</h3>'


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        if not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure repeat password was submitted
        if not request.form.get("confirmation"):
            return apology("must repeat the password", 400)

        # Ensure passwords match
        if not checkPasswordMatch():
            return apology("Passwords dont match", 400)

        # Query database for username
        users = db_con.cursor().execute(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
        ).fetchall()

        # print(users)
        # Ensure username does not exist
        if len(users) > 0:
            return apology("User already exists, please login instead", 400)

        # Add user to the database
        db_con.cursor().execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            (request.form.get("username"), generate_password_hash(request.form.get("password"))),
        )
        db_con.commit()

        user = db_con.cursor().execute(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
        ).fetchone()

        # Remember which user has logged in
        session["user_id"] = user[0]
        session["user_name"] = user[1]
        session["user_initial"] = users[1][0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


def checkPasswordMatch():
    password = request.form.get("password")
    confirmation = request.form.get("confirmation")
    if confirmation == password:
        return True

    return False


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    #Forget any user_id
    session.clear()
    
     # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        users = db_con.cursor().execute(
            "SELECT * FROM users WHERE username = ?", (request.form.get("username"),)
        ).fetchall()

        # Ensure username exists and password is correct
        if len(users) != 1 or not check_password_hash(
            users[0][2], request.form.get("password")
        ):
            return apology("invalid username or password", 403)
# check_password_hash(users[0]["hash"], request.form.get("password"))
        # Remember which user has logged in
        session["user_id"] = users[0][0]
        session["user_name"] = users[0][1]
        session["user_initial"] = users[0][1][0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

def drawDate():
    todays_date = date.today()
    print('Today Date:',todays_date)
    nextFriday = todays_date + timedelta(days=-todays_date.weekday(), weeks=1)
    print('Next Friday Date:',nextFriday)
    return nextFriday
 
    