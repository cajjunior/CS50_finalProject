import re

from cs50 import SQL
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

# Customize value to Reais standards
def real(value):
    return f"R${value:,.2f}"

# run flask
app = Flask(__name__)
app.config["SESSION_PERMANET"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Custom filter
app.jinja_env.filters["real"] = real

# Define db
db = SQL("sqlite:///alphahops.db")


@app.route("/")
def index():

    # If not logged in redirect user
    if not session.get("user_id"):
        return redirect("/login")
    return render_template("index.html")

    # Set counter to blink on screen
    beer_stock = db.execute("SELECT SUM(orders) FROM orders")
    stock = beer_stock[0]["SUM(orders)"]
    # Assume total stock as 100 units
    total_stock = 100
    session["stock"] = total_stock - stock


@app.route("/order", methods=["GET", "POST"])
def order():
    # Ensure user is logged in
    if not session.get("user_id"):
        return redirect("/login")

    username = session["username"]
    order = request.form.get("order")

    # Error check
    if not order:
        return render_template("error.html", message="Missing order quantity!")

    # Avoid non positive int
    if int(order) <= 0:
        return render_template("error.html", message="Order quantity must be positive!")

    # Variables to calculate total price and update stock(counter) and place order into db
    price_db = db.execute("SELECT price FROM orders")
    price = price_db[0]["price"]
    total = int(order) * price

    # Counter
    beer_stock = db.execute("SELECT SUM(orders) FROM orders")
    stock = beer_stock[0]["SUM(orders)"] + int(order)
    # Assume total stock as 100 units
    total_stock = 100
    session["stock"] = total_stock - stock
    counter = session["stock"]

    # if sold out
    if beer_stock[0]["SUM(orders)"] == 100:
            # reset counter without last order
            session["stock"] = total_stock - beer_stock[0]["SUM(orders)"]
            return render_template("error.html", message="Sorry, SOLD OUT!")


    # If not enough stock
    if stock > total_stock:
            # reset counter without last order
            session["stock"] = total_stock - beer_stock[0]["SUM(orders)"]
            return render_template("error.html", message="Sorry, quantity is over stock. Check stock quantity and order again!")

    # Insert into db new order
    db.execute("INSERT INTO orders (name, orders, total) VALUES(?, ?, ?)", username, order, total)

    # redirect to my order page
    return redirect("/orders")


@app.route("/orders")
def orders():
    # Ensure user is logged in
    if not session.get("user_id"):
        return redirect("/login")

    # Run db to show users orders
    username = session["username"]
    orders = db.execute("SELECT * FROM orders WHERE name = ? ORDER BY time DESC", username)
    return render_template("orders.html", orders=orders)


@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # Counter
    beer_stock = db.execute("SELECT SUM(orders) FROM orders")
    stock = beer_stock[0]["SUM(orders)"]
    session["stock"] = 100 - stock

    # Get info by POST method
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("error.html", message="Must provide username!")

        # Ensure password was submitted
        if not request.form.get("password"):
            return render_template("error.html", message="Must provide password!")

        # run db to get users info
        rows = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("error.html", message="Invalid username and/or password")

        # Remember user id and username
        session["user_id"] = rows[0]["id"]
        session["username"] = rows[0]["username"]

        return redirect("/")
    # If GET method
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    # clear session
    session["user_id"] = None
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():

    # Forget any user_id
    session.clear()

    # Register User reached via POST method
    if (request.method == "POST"):
        # match "name" field in html code ("name=username")
        username = request.form.get("username")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted (blank)
        if not username:
            return render_template("error.html", message="Must provide username!")

        # Ensure email and phone was submitted (blank)
        if not email or not phone:
            return render_template("error.html", message="Must provide phone and email!")

        # Ensure username is unique
        users = db.execute("SELECT username FROM users")

        for user in users:
            if user["username"] == username:
                return render_template("error.html", message="Username already exists!")

        # Password conditions (at least 6 characters including 1 capital letter and 1 number)
        if len(password) < 6:
            return render_template("error.html", message="Your password must have at least 6 characters!")
        elif re.search("[0-9]", password) is None:
            return render_template("error.html", message="You must have a number in your password!")
        elif re.search("[A-Z]", password) is None:
            return render_template("error.html", message="You must have a capital letter in you password!")

        # Ensure password was submitted
        elif not password:
            return render_template("error.html", message="Password is required!")

        # Ensure confirmation password was submitted
        elif not confirmation:
            return render_template("error.html", message="Password confirmation is required!")

        # Ensure password matches
        if password != confirmation:
            return render_template("error.html", message="Password must match!")

        # Hash function // generate hash password
        hash = generate_password_hash(password)

        # Try /excecpt condition to check if user exists
        try:
            # Insert data in database using hash password
            db.execute("INSERT INTO users (username, email, phone, hash) VALUES (?, ?, ?, ?)", username, email, phone, hash)
            return redirect("/")
        except:
            return render_template("error.html", message="Username already exists!")

    else:
        return render_template("register.html")

