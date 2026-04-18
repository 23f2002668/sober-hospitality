import subprocess, os, glob
#subprocess.run("pip install --upgrade pip", shell=True)
#subprocess.run("pip install -r requirements.txt", shell=True)

import sqlite3, random, time, json, statistics, base64, csv
from flask_cors import CORS
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from passlib.hash import sha256_crypt
from werkzeug.utils import secure_filename
from flask import Flask, render_template, url_for, redirect, session, json, jsonify, request, current_app, send_file

# Object for FLASK App
app = Flask(__name__)

# Enable CORS globally
CORS(app)

# Secret Key
# Purpose ==> 1. Session Management,  2. CSRF Protection  &  3. Signing Cookies
app.secret_key = "XaITbfghe@4591RRTUCDSfdkodg&8249rut774360@#dhfu$hfhfk"

# Sqlite Database File for restaurant-management
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///restaurant-management.sqlite3"

# Enable SQLALCHEMY to Track Changes/Modifications to Objects
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True

# Initialize SQLALCHEMY
db = SQLAlchemy(app)

# Database Tables
class RESTAURANTS(db.Model):
    __tablename__ = "RESTAURANTS"
    SrNo = db.Column(db.INTEGER, autoincrement=True)
    RestaurantName = db.Column(db.String(20))
    RestaurantId = db.Column(db.String(20), unique=True, primary_key=True)
    RestaurantUsername = db.Column(db.String(50), unique=True)
    RestaurantEmail = db.Column(db.String(50), unique=True)
    RestaurantMobile = db.Column(db.String(15), unique=True)
    RestaurantCountry = db.Column(db.String(100))
    RestaurantState = db.Column(db.String(100))
    RestaurantDistrict = db.Column(db.String(100))
    RestaurantCity = db.Column(db.String(100))
    RestaurantStreet = db.Column(db.String(100))
    RestaurantPropertyNo = db.Column(db.String(10))
    RestaurantPassword = db.Column(db.String(256))
    StatusId = db.Column(db.String(20), db.ForeignKey('RESTAURANT_STATUS.StatusId'))
    Timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class DISH_CATEGORIES(db.Model):
    __tablename__ = "DISH_CATEGORIES"
    SrNo = db.Column(db.INTEGER, autoincrement=True)
    CategoryName = db.Column(db.String(20))
    CategoryId = db.Column(db.String(20), unique=True, primary_key=True)


class DISHES(db.Model):
    __tablename__ = "DISHES"
    SrNo = db.Column(db.INTEGER, autoincrement=True)
    DishName = db.Column(db.String(20))
    DishId = db.Column(db.String(20), unique=True, primary_key=True)
    DishPrice = db.Column(db.Numeric(10,2))

class TABLES(db.Model):
    __tablename__ = "TABLES"
    SrNo = db.Column(db.INTEGER, autoincrement=True)
    TableName = db.Column(db.String(20), unique=True)
    TableId = db.Column(db.String(20), unique=True, primary_key=True)
    StatusId = db.Column(db.String(20), db.ForeignKey('TABLE_STATUS.StatusId'))

class CUSTOMERS(db.Model):
    __tablename__ = "CUSTOMERS"
    SrNo = db.Column(db.INTEGER, autoincrement=True)
    CustomerName = db.Column(db.String(20))
    CustomerMobile = db.Column(db.String(15), unique=True, primary_key=True)
    #LoyaltyPoints = db.Column(db.String(10))
    Timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ORDERS(db.Model):
    __tablename__ = "ORDERS"
    SrNo = db.Column(db.INTEGER, autoincrement=True, unique=True)
    OrderId = db.Column(db.String(20), unique=True, primary_key=True)
    RestaurantId = db.Column(db.String(20), db.ForeignKey('RESTAURANTS.RestaurantId'))
    TableId = db.Column(db.String(20), db.ForeignKey('TABLES.TableId'))
    CustomerMobile = db.Column(db.String(15), db.ForeignKey('CUSTOMERS.CustomerMobile'))
    Timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class ORDER_ITEMS(db.Model):
    __tablename__ = "ORDER_ITEMS"
    SrNo = db.Column(db.INTEGER, autoincrement=True, primary_key=True)
    OrderId = db.Column(db.String(20), db.ForeignKey('ORDERS.OrderId'), nullable=False)
    DishId = db.Column(db.String(20), db.ForeignKey('DISHES.DishId'), nullable=False)
    Quantity = db.Column(db.INTEGER, nullable=False, default=1)
    DishPrice = db.Column(db.Numeric(10,2))
    TotalPrice = db.Column(db.Numeric(10,2))
    SpecialRequests = db.Column(db.String(500))

class PAYMENTS(db.Model):
    __tablename__ = "PAYMENTS"
    SrNo = db.Column(db.INTEGER, autoincrement=True)
    PaymentId = db.Column(db.String(20), unique=True, primary_key=True)
    OrderId = db.Column(db.String(20), db.ForeignKey('ORDERS.OrderId'))
    TotalBill = db.Column(db.Numeric(10,2))
    StatusId = db.Column(db.String(20), db.ForeignKey('PAYMENT_STATUS.StatusId'))
    Timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class PAYMENT_STATUS(db.Model):
    __tablename__ = "PAYMENT_STATUS"
    SrNo = db.Column(db.INTEGER, autoincrement=True)
    Status = db.Column(db.String(20))
    StatusId = db.Column(db.String(20), unique=True, primary_key=True)
    Timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class TABLE_STATUS(db.Model):
    __tablename__ = "TABLE_STATUS"
    SrNo = db.Column(db.INTEGER, autoincrement=True)
    Status = db.Column(db.String(20))
    StatusId = db.Column(db.String(20), unique=True, primary_key=True)
    Timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class RESTAURANT_STATUS(db.Model):
    __tablename__ = "RESTAURANT_STATUS"
    SrNo = db.Column(db.INTEGER, autoincrement=True)
    Status = db.Column(db.String(20))
    StatusId = db.Column(db.String(20), unique=True, primary_key=True)
    Timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class RESTAURANT_INFO(db.Model):
    __tablename__ = "RESTAURANT_INFO"
    SrNo = db.Column(db.INTEGER, autoincrement=True, unique=True, primary_key=True)
    RestaurantId = db.Column(db.String(50), db.ForeignKey('RESTAURANTS.RestaurantId'))
    CategoryId = db.Column(db.String(20), db.ForeignKey('DISH_CATEGORIES.CategoryId'))
    DishId = db.Column(db.String(20), db.ForeignKey('DISHES.DishId'))
    TableId = db.Column(db.String(20), db.ForeignKey('TABLES.TableId'))

class BILLING(db.Model):
    __tablename__ = "BILLING"
    SrNo = db.Column(db.INTEGER, autoincrement=True, unique=True, primary_key=True)
    CustomerMobile = db.Column(db.String(15), db.ForeignKey('CUSTOMERS.CustomerMobile'))
    RestaurantId = db.Column(db.String(50), db.ForeignKey('RESTAURANTS.RestaurantId'))
    TableId = db.Column(db.String(20), db.ForeignKey('TABLES.TableId'))
    OrderId = db.Column(db.String(20), db.ForeignKey('ORDERS.OrderId'))
    TotalBill = db.Column(db.String(20))
    PaymentId = db.Column(db.String(20), db.ForeignKey('PAYMENTS.PaymentId'))
    Timestamp = db.Column(db.DateTime, default=datetime.utcnow)

# Create the Defined Tables
'''@app.before_request
def CreateTable():
    db.create_all()
'''

# Routes

@app.route("/", methods=["GET", "POST"])
def home():
    return render_template("home.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    return render_template("login.html")

@app.route("/customer", methods=["GET", "POST"])
def customer():
    return render_template("customer.html")

@app.route("/restaurant-admin", methods=["GET", "POST"])
def restaurant_admin():
    return render_template("restaurant-admin.html")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✓ Database tables created")
    app.debug=True
    app.run(host="0.0.0.0", port=8000)