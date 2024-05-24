from flask import Flask, jsonify, request #pip install flask
from flask_sqlalchemy import SQLAlchemy #pip install flask-sqlalchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session # PIP INSTALL SQLALCHEMY
from sqlalchemy import select
from flask_marshmallow import Marshmallow #PIP INSTAL FLASK-MARSHMALLOW
from marshmallow import fields, validate, ValidationError
from typing import List
import datetime


# categorically, clearly, correctly, 
# definitely, especially, exactly, 
# explicitly, individually, pointedly, 
# precisely, respectively

app = Flask(__name__)
# configures out application so it can find our databse using the SQLALCHEMY_DATABASE_URI key in the config object
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:Carmen!1994@localhost/e_commerce_db2"

# creating a Base class that inherits the DelcarativeBase from sqlalchemy.orm
# provides functionality for creating python classes that will become tables
# in our database
# ALL classes we create will inherit from the Base class
class Base(DeclarativeBase):
    pass

# istantiats Flask-SQLAlchemy
# creates an instance of SQLAlchemy that we pass our flask application too
# and then specify the class to use for model building - python classes that become SQL Tables
db = SQLAlchemy(app, model_class=Base)
ma = Marshmallow(app)

# Creating Models - Class that becomes a table in our database
class Customer(Base):
    # the name of our table when it makes over to SQL
    __tablename__ = "Customers"
    # column_name - Mapped to translate the python type to our SQL type int to INTEGER or str to VARCHAR
    # mapped_column - providing any additional constraints to the column - primary_key, nullable, character limits etc...
    customer_id: Mapped[int] = mapped_column(autoincrement=True, primary_key = True)
    name: Mapped[str] = mapped_column(db.String(255)) #VARCHAR(255) in sql
    email: Mapped[str] = mapped_column(db.String(320))
    phone: Mapped[str] = mapped_column(db.String(15))
    # One-to-one relationship
    customer_account: Mapped["CustomerAccount"] = db.relationship(back_populates="customer")
    # ties the customer_account attribute to the CustomerAccount class
    # allow us to see CustomerAccount info through the customer object
    # create the one-to-many relationship with the orders table
    orders: Mapped[List["Order"]] = db.relationship(back_populates="customer")
    # orders is a list of Order objects
class CustomerAccount(Base):
    __tablename__ = "Customer_Accounts"
    account_id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    username: Mapped[str] = mapped_column(db.String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey("Customers.customer_id"))
    # One-to-one relationshop between customer and customer_account
    customer: Mapped['Customer'] = db.relationship(back_populates="customer_account")

order_product = db.Table(
    "Order_Product",
    Base.metadata,
    db.Column("order_id", db.ForeignKey("Orders.order_id"), primary_key=True),
    db.Column("product_id", db.ForeignKey("Products.product_id"), primary_key=True)
)

class Order(Base):
    __tablename__ = "Orders"
    order_id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    date: Mapped[datetime.date] = mapped_column(db.Date, nullable=False)
    customer_id: Mapped[int] = mapped_column(db.ForeignKey('Customers.customer_id'))
    # many-to-one relationship with the customer table
    customer: Mapped["Customer"] = db.relationship(back_populates="orders")
    products: Mapped[List["Product"]] = db.relationship(secondary=order_product)

class Product(Base):
    __tablename__ = "Products"
    product_id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)
# association table for orders and products because 
# there is a many to many relationship


# create all tables 
with app.app_context(): #gives the db access to our current instance of the app
    db.create_all()


#Schemas
class CustomerSchema(ma.Schema):
    customer_id = fields.Integer(required=False)
    name = fields.String(required=True)
    email = fields.String(required=True)
    phone = fields.String(required=True)
    
    class Meta:
        fields = ("customer_id", "name", "email", "phone")


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)


@app.route("/")
def home():
    return "JUST MAKING SURE ITS RUNNING AND PRINTING :) "

# ============================= API ROUTES =========================
# for GET-ing ONE single customer
# @app.route("/customers/<int:customer_id>", methods = ["GET"])
# def get_customers(customer_id):

# GET -ing customers
@app.route("/customers", methods = ["GET"])
def get_customers():
    # we're using the class Customer as a model for the Customers table
    query = select(Customer) #creates a SELECT query for the customer table SELECT * FROM Customers
    result = db.session.execute(query).scalars() #sequence of customer objects, rather than a list of rows or tuples
    print(result)
    customers = result.all() #Fetches all rows of data from the result

    # convert customers through the marshmallow schema and return the response
    return customers_schema.jsonify(customers)



#POST -ing a customer
@app.route("/customers", methods=["POST"])
def add_customer():
    try:
        #validate that the incoming data matches our schema
        customer_data = customer_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    with Session(db.engine) as session: #creates a session object, allowing us to make changes to our database
        with session.begin(): #begin a transaction with the database - creates a transaction to interact with the database
            name = customer_data['name']
            email = customer_data['email']
            phone = customer_data['phone']
            #using information from the request to instantiate our Customer class
            new_customer = Customer(name=name, email=email, phone=phone)
            # adding the new_customer object to the db
            session.add(new_customer)
            session.commit()
    return jsonify({"message": "New customer added successfully"}), 201 #resources was created on the server




if __name__ == "__main__":
    app.run(debug=True)