import os
import re

from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import check_password_hash, generate_password_hash

def real(value):
    return f"R${value:,.2f}"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-secret-key")
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///alphahops.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
Session(app)

app.jinja_env.filters["real"] = real

db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    hash = db.Column(db.String(256), nullable=False)


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    orders = db.Column(db.Integer, nullable=False)
    total = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, default=0.0)
    time = db.Column(db.DateTime, server_default=db.func.now())


with app.app_context():
    db.create_all()


BEER_PRICE = 25.0
TOTAL_STOCK = 100


def get_stock_used():
    result = db.session.query(db.func.sum(Order.orders)).scalar()
    return result or 0


@app.route("/")
def index():
    if not session.get("user_id"):
        return redirect("/login")
    return render_template("index.html")


@app.route("/order", methods=["GET", "POST"])
def order():
    if not session.get("user_id"):
        return redirect("/login")

    username = session["username"]
    order_qty = request.form.get("order")

    if not order_qty:
        return render_template("error.html", message="Missing order quantity!")

    if int(order_qty) <= 0:
        return render_template("error.html", message="Order quantity must be positive!")

    stock_used = get_stock_used()
    new_stock_used = stock_used + int(order_qty)

    if stock_used >= TOTAL_STOCK:
        session["stock"] = 0
        return render_template("error.html", message="Sorry, SOLD OUT!")

    if new_stock_used > TOTAL_STOCK:
        session["stock"] = TOTAL_STOCK - stock_used
        return render_template("error.html", message="Sorry, quantity is over stock. Check stock quantity and order again!")

    total = int(order_qty) * BEER_PRICE
    session["stock"] = TOTAL_STOCK - new_stock_used

    new_order = Order(name=username, orders=int(order_qty), total=total, price=BEER_PRICE)
    db.session.add(new_order)
    db.session.commit()

    return redirect("/orders")


@app.route("/orders")
def orders():
    if not session.get("user_id"):
        return redirect("/login")

    username = session["username"]
    user_orders = Order.query.filter_by(name=username).order_by(Order.time.desc()).all()
    orders_data = [{"name": o.name, "orders": o.orders, "total": o.total, "price": o.price, "beer_name": "Summer Ale", "time": o.time} for o in user_orders]
    return render_template("orders.html", orders=orders_data)


@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()

    stock_used = get_stock_used()
    session["stock"] = TOTAL_STOCK - stock_used

    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("error.html", message="Must provide username!")

        if not request.form.get("password"):
            return render_template("error.html", message="Must provide password!")

        user = User.query.filter_by(username=request.form.get("username")).first()

        if not user or not check_password_hash(user.hash, request.form.get("password")):
            return render_template("error.html", message="Invalid username and/or password")

        session["user_id"] = user.id
        session["username"] = user.username

        return redirect("/")
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    session["user_id"] = None
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    session.clear()

    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        phone = request.form.get("phone")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        if not username:
            return render_template("error.html", message="Must provide username!")

        if not email or not phone:
            return render_template("error.html", message="Must provide phone and email!")

        if User.query.filter_by(username=username).first():
            return render_template("error.html", message="Username already exists!")

        if len(password) < 6:
            return render_template("error.html", message="Your password must have at least 6 characters!")
        elif re.search("[0-9]", password) is None:
            return render_template("error.html", message="You must have a number in your password!")
        elif re.search("[A-Z]", password) is None:
            return render_template("error.html", message="You must have a capital letter in your password!")
        elif not confirmation:
            return render_template("error.html", message="Password confirmation is required!")

        if password != confirmation:
            return render_template("error.html", message="Password must match!")

        hashed = generate_password_hash(password, method="pbkdf2:sha256")

        try:
            new_user = User(username=username, email=email, phone=phone, hash=hashed)
            db.session.add(new_user)
            db.session.commit()
            return redirect("/")
        except Exception:
            db.session.rollback()
            return render_template("error.html", message="Username already exists!")

    else:
        return render_template("register.html")
