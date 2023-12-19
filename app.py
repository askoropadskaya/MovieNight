from datetime import date, datetime, timedelta, timezone
import random
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3

from helpers import apology, login_required

NOT_VOTED_YET = 0
VOTED_NOT_SELECTED = 1
VOTED_SELECTED = 2

app = Flask(__name__)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db_con = sqlite3.connect("movienight.db", check_same_thread=False)
create_users_table = "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, username VARCHAR (15) NOT NULL, hash VARCHAR (20) NOT NULL);"
create_votes_table = "CREATE TABLE IF NOT EXISTS votes (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL, movie_name TEXT NOT NULL, timestamp TEXT NOT NULL, status INTEGER NOT NULL, poster_url TEXT NOT NULL);"
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

    winner_vote = db_con.cursor().execute(
            "SELECT * FROM votes WHERE timestamp = ? AND status = ?", (today, VOTED_SELECTED)
        ).fetchone()
    draw_button_enabled = len(all_votes) > 0 and winner_vote is None

    if request.method == "GET":
        return render_template(
            "homepage.html", 
            voted=voted, 
            vote=vote, 
            today=today, 
            all_votes=all_votes, 
            draw_button_enabled=draw_button_enabled,
            winner_vote=winner_vote
        )
        
    if request.method == "POST":
        if vote is not None and vote[4] != NOT_VOTED_YET:
            return apology("Can't change vote after DRAW", 400)

        if not request.form.get("moviename"):
            return apology("Please, provide movie name", 400)
        
        if not request.form.get("poster_url"):
            return apology("Please, provide poster url", 400)
        
        if voted:
            db_con.cursor().execute(
                "UPDATE votes set movie_name = ?, poster_url = ? WHERE id = ?", (request.form.get("moviename"), request.form.get("poster_url"), vote[0])
            )
            db_con.commit()
        else:
            db_con.cursor().execute(
                "INSERT into votes (user_id, movie_name, timestamp, status, poster_url) VALUES(?,?,?,?,?)", (session["user_id"],request.form.get("moviename"),  today, NOT_VOTED_YET, request.form.get("poster_url"))
            )
            db_con.commit()
        return redirect("/")    


@app.route("/draw", methods=["POST"])
@login_required
def draw():
    today = date.today()
    all_votes = db_con.cursor().execute(
        "SELECT * FROM votes WHERE timestamp = ?", (today,)
    ).fetchall()

    if any([voted(v) for v in all_votes]):
        return redirect("/")
    
    winner_index = random.randint(0, len(all_votes) - 1)
    winner_id = all_votes[winner_index][0]
    for v in all_votes:
        if v[0] == winner_id: status = VOTED_SELECTED 
        else: status = VOTED_NOT_SELECTED
        db_con.cursor().execute(
            "UPDATE votes set status = ? WHERE id = ?", (status, v[0])
        )
        db_con.commit()
    return redirect("/")


def voted(vote):
    return vote[4] != NOT_VOTED_YET

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
        
        # Remember which user has logged in
        session["user_id"] = users[0][0]
        session["user_name"] = users[0][1]
        session["user_initial"] = users[0][1][0]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
 
@app.route("/about", methods=["GET"])
def about():
    return render_template("about.html")