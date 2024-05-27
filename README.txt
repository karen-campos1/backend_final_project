# E-Commerce Flask API

This is a Flask-based API for an e-commerce application, providing endpoints for managing customers, customer accounts, products, and orders.

## Table of Contents

- Installation
- Configuration
- Running the Application
- API Endpoints
  - Customers
  - Products
  - Orders
  - Customer Accounts
- Dependencies

## Installation
1. Clone the repository: 
https://github.com/karen-campos1/backend_final_project.git

2. INSTALL the required Dependencies:

To install requirements.txt on MAC:
pip3 install -r requirements

To install requirements.txt on PC:
pip install -r requirements

To create and activate a virtual environment:

For MAC users:
python3 -m venv venv
source venv/bin/activate


## Configuration

1. Update the database connection string in the app.config: (NOTE insert your password in the capitalized text reading YOUR-PASSWORD-HERE, after colon : and before @ sign. )
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:YOUR-PASSWORD-HERE@localhost/e_commerce_db2"


## Running the Application
1. you must run the Flask application in your terminal (or depending on your setup you can hit the run button):
python app.py 

2. The application will be available at http://localhost:5000.

## API Endpoints

Customers:
GET /customers

Get a list of all customers.
Example response:
json
Copy code
[
  {
    "customer_id": 1,
    "name": "Jane Doe",
    "email": "jane.doe@gmail.com",
    "phone": "123-456-7890"
  }
]
POST /customers

Add a new customer.
Request body:
json
Copy code
{
  "name": "Jane Doe",
  "email": "jane.doe@example.com",
  "phone": "098-765-4321"
}
Example response:
json
Copy code
{
  "message": "New customer added successfully"
}
PUT /customers/int:customer_id

Update an existing customer's details.
Request body:
json
Copy code
{
  "name": "Jane Smith",
  "email": "jane.smith@yahoo.com",
  "phone": "111-222-3333"
}
Example response:
json
Copy code
{
  "message": "Customer details successfully updated"
}
DELETE /customers/int:customer_id

Delete a customer.
Example response:
json
Copy code
{
  "message": "Customer removed successfully!"
}
Products
GET /products

Get a list of all products.
Example response:
json
Copy code
[
  {
    "product_id": 1,
    "name": "Product 1",
    "price": 19.99
  }
]
POST /products

Add a new product.
Request body:
json
Copy code
{
  "name": "Product 2",
  "price": 29.99
}
Example response:
json
Copy code
{
  "Message": "New product successfully added!"
}
PUT /products/int:product_id

Update an existing product's details.
Request body:
json
Copy code
{
  "name": "Updated Product Name",
  "price": 39.99
}
Example response:
json
Copy code
{
  "message": "Product details successfully updated!"
}
DELETE /products/int:product_id

Delete a product.
Example response:
json
Copy code
{
  "message": "Product successfully deleted!"
}
Orders
GET /orders

Get a list of all orders.
Example response:
json
Copy code
[
  {
    "order_id": 1,
    "customer_id": 1,
    "date": "2024-05-25",
    "products": [
      {
        "product_id": 1,
        "name": "Product 1",
        "price": 19.99
      }
    ]
  }
]
POST /orders

Add a new order.
Request body:
json
Copy code
{
  "customer_id": 1,
  "date": "2024-05-25",
  "products": [
    {
      "product_id": 1,
      "name": "Product 1",
      "price": 19.99
    }
  ]
}
Example response:
json
Copy code
{
  "message": "New order successfully added!"
}
PUT /orders/int:order_id

Update an existing order's details.
Request body:
json
Copy code
{
  "customer_id": 1,
  "date": "2024-05-26",
  "products": [
    {
      "product_id": 2,
      "name": "Product 2",
      "price": 29.99
    }
  ]
}
Example response:
json
Copy code
{
  "Message": "Order was successfully updated!"
}
DELETE /orders/int:order_id

Delete an order.
Example response:
json
Copy code
{
  "message": "Order removed successfully"
}
Customer Accounts
GET /customer_accounts

Get a list of all customer accounts.
Example response:
json
Copy code
[
  {
    "account_id": 1,
    "username": "johndoe",
    "password": "hashedpassword",
    "customer_id": 1
  }
]
POST /customer_accounts

Add a new customer account.
Request body:
json
Copy code
{
  "username": "janedoe",
  "password": "password123",
  "customer_id": 1
}
Example response:
json
Copy code
{
  "message": "New customer account added successfully"
}
PUT /customer_accounts/int:account_id

Update an existing customer account's details.
Request body:
json
Copy code
{
  "username": "newusername",
  "password": "newpassword",
  "customer_id": 1
}
Example response:
json
Copy code
{
  "message": "Customer account details successfully updated!"
}
DELETE /customer_accounts/int:account_id

Delete a customer account.
Example response:
json
Copy code
{
  "message": "Customer account was deleted successfully."
}


## Dependencies:

Flask
Flask-CORS
Flask-SQLAlchemy
Flask-Marshmallow
Marshmallow
SQLAlchemy
mysql-connector-python
datetime


1. Install these dependencies using:
For PC users:
pip install flask flask-cors flask-sqlalchemy flask-marshmallow marshmallow sqlalchemy mysql-connector-python datetime


For Mac users:
pip3 install flask flask-cors flask-sqlalchemy flask-marshmallow marshmallow sqlalchemy mysql-connector-python datetime



