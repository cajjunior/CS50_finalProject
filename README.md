# ALPHAHOPS WEBSITE
#### Video Demo: <https://youtu.be/Tna4phmi-nc>

#### Description:
This is my CS50x final project!
A pre-sale website to get reservation orders and manage stock of the upcoming beers from "Alphahops Brewery".

AlphaHops is my home brewery name, a non commercial place with very limited production. Just a hobby that inspired me to develop this website as a prototype for a "real" comercial brewery.

In this website, customers can make reservation orders of the upcoming beer that will be launched. They place their orders and when the beer is ready to drink, we contact them to pick up their order!

**What the website does:**
- Register users in a database called alphahops.db (SQL);
- Handle user's unique username and hash password for security;
- Login page linked with users table on alphahops.db to manage permission to log in;
- Use "session" to register users when logged in;
- Order page is visible only for those who are logged in;
- Order page shows a quantity form in which users can place their orders;
- When orders are placed users can see their orders on a table on "My Orders" page ordered by time (last order first);
- At login and Order pages a "Blink Counter" was created to show the volume of beers in stock to aware customers;
- Program will not accept more orders then available in stock;

New users have to make a registration to log in. A database with a secure hash password function was created to get users registration.

After logging in, users can place orders by quantity. The stock counter will be automatically decreased as orders are being made.

Another table called orders was created in the database to store all transactions and each user can view his orders on the "My Orders" page.

There is a condition that stock quantity should be enough (higher or equal) to accept new orders.

Some errors checking were created as well to validate username, password, password confirmation and blank information.

Developed with Python, Flask, HTML, CSS and SQL.

Author: Carlos A. Julio Jr.
São Paulo, SP - Brazil


# Disclaimer:
This is not a real comercial website. We do not sell beers!
This website was developed as a prototype for the only purpose to accomplish the CS50x final project.
Alphahops is not a commercial brewery.


# Files

## application.py

This is the controller file of the website, where you will find functions implemented using flask to run the app integrated with a SQL database.

Atop of the file are a bunch of imports.
    - re to deal with regular expressions;
    - CS50 SQL to work with SQL in CS50 IDE;
    - Flask to run the app with important modules like Session;
    - werkzeug to deal with hash password function.

- Before starting flask configuration you will notice a function called "real" that uses Jinja filters syntax to format a numeric value when displayed in html, in this case to Real standards.

- Then, you will see some configuration to run Flask app, using “filesytem” as session type and calling up Session(app).

- A database is defined using SQL, called alphahops.db

Now, the routes as follow with some important notes:

@app.route("/")

    Defines index functions:
        - Begins with an if condition to check if users are logged in session, if not they are redirected to login, else they go to index (order page).
        - Then some variables are defined to set up the counter to blink on the screen by selecting the sum of orders in the database and subtracting it from the total stock.

@app.route("/order)

    Defines order functions:
        - Ensure user is logged in using if condition and "Session";
        - Deals with error checking to guarantee volume is positive and not higher than available in stock;
        - Some variables are defined to calculate total price to be inserted on the database;
        - Counter has to be updated here every time users place orders;
        - If stock enough, order will be placed and database will be executed to have the information inserted;
        - Finally, users will be redirected to the "My orders" page where they can view their orders history.

@app.route("/orders")

    Defines orders functions:
        - Ensure user is logged in using "Session";
        - Runs orders table in alphahops.db to display users orders history.

@app.route("/login")

    Defines login functions:
        - Begins cleaning session to forget any user id;
        - Counter is set to be displayed;
        - Then, POST method condition is set to validate user and password;
        - If valid, next step is to run the database to ensure username and hash password is correct;
        - Finally, we store the user id and username into session to query his/her data information when logged in;
        - When logged in, the user is redirected to the index to place orders.

@app.route("/logout")

    Defines log out functions:
        - Clear session setting "user id" to "None"

@ app.route("/register")

    Defines register functions:
        - Similar to Log in, POST method condition is set to validate registration's username, email, phone, password and password confirmation;
        - Ensure username is unique by running database table "users" with a "for" loop on it;
        - Password conditions are set as follows using if conditions. Password must have at least 6 characters including one number and one capital letter;
        - Ensure password was submitted and matches;
        - Generate hash password using "generate_password_hash" imported from "werkzeug.security";
        - Make use of "try/except" condition to guarantee that the user does not exist in the database before inserting the new user into users table in alphahops.db.


## requirements.txt
This file shows the packages on which this app/website will depend.


## alphahops.db
This database was created as SQL and it contains two tables, users and orders.

    1. users

    Created to register customers information, which are:
        > id (Primary key);
        > username (text)
        > hash (text) = hash password generated in application.py
        > email (text)
        > phone (integer)

    2. orders

    Created to register all transaction from users, it contains:
        > id (Primary key)
        > name (text) which refers to the username registered
        > orders (int) that is the quantity ordered by the customer by each submit order
        > total (num) is the total price to pay
        > time (timestamp) store time of orders
        > beer_name (text) is the name of the beer (default value)
        > price (num) is the price of the beer which has also a default value


# static

## **styles.css**

This file is responsible for styling the website by describing how certain attributes of HTML elements should be modified.

One nice thing to look at is the Blink set up (stock counter that blinks the actual volume of stock).

The design is based on three main block defined as the follow classes:

    .container
        Holds the beer background of the website.

    . info
        White with little yellow division that carries all beer elements

    .summeAle
        Stylization for the beer information

    .beer_info
        Yellow background for beer division and stylization to hold information, form and tables

    .summer
        Summer Ale label image setup

    .body
        Stylization of body with selected font from google fonts

    p, h1, h4, h5
        Stylization of elements to get darker due to opacity effects

    nav .navbar-brand>img
        Deal with size of brand logo

    .counter
       Stylization from blink

    .blink
        Stylization and set up of blink

    @keyframes blink
        Blink keyframes setup


# templates

## **layout.html**

This template carries all the "head" and the "body" settings which will be extended with "navbar" (responsive mobile friendly menus), on the next html files.

    head
        - You will notice a meta tag for "utf-8" standards and "viewport" to deal with responsive matters.
        - A link to stylesheet (styles.css) and some links of Bootstrap due to stylization.
        - Also you will find a family font imported by google fonts called 'Dosis'.

    body

        - Holds the brand logo;
        - Carry the navigation menu bar using "Navbar" (mobile friendly) also from Bootstrap. Routes/pages are: Order Now, My Orders, Login, Register, Logout.
        - A for loop using Jinja syntax to show different menus when logged in and logged out;
        - A beer background image for the body;
        - The Summer Ale beer label image to make more attractive;

    footer
        - At the very end a footer was created to make a disclaimer about the project making clear that it is not a real comercial website.

## **index.html**

This is the homepage in which the user can make orders. Also can be found as "Order now" on the menu, after logged in.

    This templates extends layout.html and its body contains on separate "divs":

        - An if condition using Jinja syntax to say customized Hello using user´s username;
        - Log out option;

        - Text containing information about the beer;
        - Form to get order quantity using "min 1" and "required" field to get only positive numbers(you will see an error check as well at application.py);

        - A stock counter to aware customers of the actual volume;
        - Text explaining how presale works;

## **login.html**

This template follows the same design of index.html but instead of displaying an order quantity form there is a login form.

    - Login form;
    - Ensure user´s input "username" and "password" using "required" field on html and controlled by application.py as well;
    - After logged in users are redirect to index.html to place their orders (if user exists in database);
    - Routes to Register available below Submit button and on Menu;
    - Stock counter to motivate buyers to login or register for an account;

## **orders.html**

This template shows a table with all orders placed by the user when logged in.

    - Extends layout;
    - Takes advantage of Jinja syntax using a "for loop" to show table with orders values
    - Notice that there is also a Jinja filter implemented to "convert" the value into "Real" standard.

## **register.html**

Similar to Log in but with a larger form instead and not displaying the beer information.

    - Text to explain password rules which are controlled by application.py;

    - Form fields:
        - Username: must be unique (it will be checked by application.py if exist in alphahos.db, table users);
        - Email: text field;
        - Phone: int field;
        - Password: "must have 6 characters, including one number and one capital letter" (controlled by application.py);
        - Password confirmation: double check password;
        - Register button takes users to the Login page where their session will be stored after logged in.

## **error.html**

This template is very useful to carry message errors by using {{ message }} sintax from Jinja.

This message will be displayed according to what happens on application.py, take a look there to see when the field "message" is called.


## Author

- Github: [@cajjunior](https://www.github.com/cajjunior)
- Linked in: [@carlosalbertojuliojunior](https://www.linkedin.com/in/carlosalbertojuliojunior/)

