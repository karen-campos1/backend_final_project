from flask import Flask, jsonify, request #pip install flask
from flask_cors import CORS # pip install flask-cors
from flask_sqlalchemy import SQLAlchemy #pip install flask-sqlalchemy
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, Session # PIP INSTALL SQLALCHEMY
from sqlalchemy import select, delete #queries translated to python
from flask_marshmallow import Marshmallow #PIP INSTAL FLASK-MARSHMALLOW
from marshmallow import fields, validate, ValidationError
from typing import List
import datetime


# categorically, clearly, correctly, 
# definitely, especially, exactly, 
# explicitly, individually, pointedly, 
# precisely, respectively

app = Flask(__name__)
cors = CORS(app) #Cross Origin Resource Sharing - allows external applications to make requests to our flask app
# configures out application so it can find our databse using the SQLALCHEMY_DATABASE_URI key in the config object
app.config['SQLALCHEMY_DATABASE_URI'] = "mysql+mysqlconnector://root:Carmen!1994@localhost/e_commerce_db2"
app.json.sort_keys = False

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
    customer_account: Mapped["CustomerAccount"] = db.relationship(back_populates="customer", uselist=False)
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
    products: Mapped[List["Product"]] = db.relationship(secondary=order_product, back_populates="orders", cascade="all, delete")

class Product(Base):
    __tablename__ = "Products"
    product_id: Mapped[int] = mapped_column(autoincrement=True, primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    price: Mapped[float] = mapped_column(db.Float, nullable=False)
    orders: Mapped[List["Order"]] = db.relationship(secondary=order_product, back_populates="products")
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


@app.route('/customers/<int:customer_id>', methods=["PUT"])
def updated_customer(customer_id):
    with Session(db.engine) as session:#Creates a session object using the SQLAlchmey Enginge
        with session.begin(): #Begins transaction   
            #retrieve a customer with the customer_id passed in from the request
            query = select (Customer).filter(Customer.customer_id == customer_id)
            result = session.execute(query).scalars().first()   #returns query results as an object, and grabs the first record returned
            if result is None:
                return jsonify({"error": "Customer not found"}), 404
            
            customer = result #naming the customer variable that we're working with
            # customer object
            try:
                customer_data = customer_schema.load(request.json)
                
            except ValidationError as err:
                return jsonify(err.messages), 400
            
            #update the customer attributes
            for field, value in customer_data.items():
                setattr(customer, field, value)
                
            session.commit() #save changes to our db
            return jsonify({"message": "Customer details successfully updated"}), 200



@app.route("/customers/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    # delete statement where we delete from the customer table where customer_id parameter
    # matches an id within the database
    delete_statement = delete(Customer).where(Customer.customer_id==customer_id)
    with db.session.begin():
        # execute the delete statement
        result = db.session.execute(delete_statement)

        #check if the customer existed to delete 
        if result.rowcount==0: #checking that no rows were returned from the delete
            return jsonify({"error": "Customer not found"}), 404
        
        return jsonify({"message": "Customer removed successfully!"})
  
        
           
class ProductSchema(ma.Schema):
    product_id = fields.Integer(required=False)
    name = fields.String(required=True, validate=validate.Length(min=1))
    price = fields.Float(required=True, validate=validate.Range(min=0))

    class Meta:
        fields = ("product_id", "name", "price")

product_schema = ProductSchema()
products_schema = ProductSchema(many=True)

# WORKING WITH OUR PRODUCTS
# adding a product
@app.route('/products', methods=["POST"])
def add_product():
    try:
        product_data = product_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400

    with Session(db.engine) as session:
        with session.begin():
            # new_product = Product(**product_data)
            new_product = Product(name=product_data['name'], price=product_data['price'])
            session.add(new_product)
            session.commit()

    return jsonify({"Message": "New product successfully added!"}), 201 #new resource has been created



@app.route('/products', methods=["GET"])
def get_products():
    query = select(Product) #SELECT * FROM Product
    result = db.session.execute(query).scalars()
    products = result.all()

    return products_schema.jsonify(products)

# get product by name
@app.route("/products/by-name", methods=["GET"])
def get_product_by_name():
    name = request.args.get("name")
    search = f"%{name}%" #% is a wildcard
    # use % with LIKE to find partial matches
    query = select(Product).where(Product.name.like(search)).order_by(Product.price.asc())

    products = db.session.execute(query).scalars().all()

    return products_schema.jsonify(products)
    

@app.route("/products/<int:product_id>", methods=["PUT"])
def update_product(product_id):
    with Session(db.engine) as session:
        with session.begin():
            query = select(Product).filter(Product.product_id == product_id)
            result = session.execute(query).scalar()  # the same as scalars().first() - first result in the scalars object
            print(result)            
            
            if result is None:
                return jsonify({"error": "Product not found!"}), 404
            product = result
            try:
                product_data = product_schema.load(request.json)
            except ValidationError as err:
                return jsonify(err.messages), 400
            
            for field, value in product_data.items():
                setattr(product, field, value)

            session.commit()
            return jsonify({"message": "Product details succesfully updated!"}), 200


@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_product(product_id):
    delete_statement = delete(Product).where(Product.product_id==product_id)
    with db.session.begin():
        result = db.session.execute(delete_statement)
        if result.rowcount == 0:
            return jsonify({"error" "Product not found"}), 404

        return jsonify({"message": "Product successfully deleted!"}), 200




class OrderSchema(ma.Schema):
    order_id = fields.Integer(required=False)
    customer_id = fields.Integer(required=True)
    date = fields.Date(required=True)
    products = fields.List(fields.Nested(ProductSchema))

    class Meta:
        fields = ("order_id", "customer_id", "date", "products")
        
order_schema = OrderSchema()
orders_schema = OrderSchema(many=True)




@app.route("/orders/<int:order_id>/add_product", methods=["POST"])
def add_product_to_order(order_id):
    data = request.get_json()
    product_id = data.get('product_id')
    
    if not product_id:
        return jsonify({"error": "Product ID is required"}), 400
    
    order = db.session.get(Order, order_id)
    product = db.session.get(Product, product_id)
    
    if not order or not product:
        return jsonify({"error": "Order or Product not found"}), 404
    
    order.products.append(product)
    db.session.commit()
    
    return jsonify({"message": "Product added to order successfully"}), 200


@app.route("/orders", methods = ["POST"])
def add_order():
    try:
        order_data = order_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    with Session(db.engine) as session:
        with session.begin():
            new_order = Order(customer_id=order_data['customer_id'], date = order_data['date'])        
            
            session.add(new_order)            
            session.commit()          
            

    return jsonify({"message": "New order successfully added!"}), 201


@app.route("/orders", methods=["GET"])
def get_orders():
    query = select(Order)
    result = db.session.execute(query).scalars()
    return orders_schema.jsonify(result)

# Get -ing ALL orders for one customer
@app.route("/orders/<int:customer_id>", methods=["GET"])
def get_customer_orders(customer_id):
    query = select(Order).filter(Order.customer_id==customer_id)
    result = db.session.execute(query).scalars()
    return orders_schema.jsonify(result)


@app.route('/orders/<int:order_id>', methods=["PUT"])
def update_order(order_id):
    with Session(db.engine) as session:
        with session.begin():
            query = select(Order).filter(Order.order_id==order_id)
            result = session.execute(query).scalar() #first result object
            if result is None:
                return jsonify({"message": "Product Not Found"}), 404
            order = result
            try:
                order_data = order_schema.load(request.json)
            except ValidationError as err:
                return jsonify(err.messages), 400
            
            for field, value in order_data.items():
                setattr(order, field, value)

            session.commit()
            return jsonify({"Message": "Order was successfully updated! "}), 200



@app.route("/orders/<int:order_id>", methods=["DELETE"])
def delete_order(order_id):
    try:
        with db.session.begin():
            # Delete associated rows in the order_product table
            delete_order_product_statement = delete(order_product).where(order_product.c.order_id == order_id)
            db.session.execute(delete_order_product_statement)
            
            # Check if the order exists before attempting to delete it
            order_query = select(Order).where(Order.order_id == order_id)
            order = db.session.execute(order_query).scalar_one_or_none()
            
            if order is None:
                return jsonify({"error": "Order not found"}), 404

            # Delete the order
            delete_order_statement = delete(Order).where(Order.order_id == order_id)
            result = db.session.execute(delete_order_statement)

            # Check if the order was deleted
            if result.rowcount == 0:
                return jsonify({"error": "Failed to delete order"}), 400

            db.session.commit()  # Commit the transaction if the order and related rows were deleted
        return jsonify({"message": "Order removed successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



class CustomerAccountSchema(ma.Schema):
    account_id = fields.Integer(required=False)
    username = fields.String(required=True, validate=validate.Length(min=3))    
    password = fields.String(required=True, validate=validate.Length(min=6))
    customer_id = fields.Integer(required=True)

    class Meta:
        fields = ("account_id", "username", "password", "customer_id")
        
customer_account_schema = CustomerAccountSchema()
customer_accounts_schema = CustomerAccountSchema(many=True)


@app.route("/customer_accounts", methods=["POST"])
def add_customer_account():
    try:
        account_data = customer_account_schema.load(request.json)
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    with Session(db.engine) as session:
        with session.begin():
            username = account_data['username']
            password = account_data['password']
            customer_id = account_data['customer_id']
            
            new_account = CustomerAccount(username=username, password=password, customer_id=customer_id)
            session.add(new_account)
            session.commit()
    
    return jsonify({"message": "New customer account added successfully"}), 201


# GET -ing (read) ONE customer account
@app.route("/customer_accounts/<int:account_id>", methods=["GET"])
def get_customer_account(account_id):  
    query = select(CustomerAccount).filter(CustomerAccount.account_id == account_id)
    result = db.session.execute(query).scalars().first()
    
    if result is None:
        return jsonify({"error": "Customer account not found"}), 404
    
    return customer_account_schema.jsonify(result)
             
# GET - ing ALL customer accounts
@app.route("/customer_accounts", methods = ["GET"])
def get_customer_accounts():
    query = select(CustomerAccount)
    result = db.session.execute(query).scalars() 
    print(result)
    customer_accounts = result.all() 

    # convert customers through the marshmallow schema and return the response
    return customer_accounts_schema.jsonify(customer_accounts)


@app.route("/customer_accounts/<int:account_id>", methods=["PUT"])
def update_customer_account(account_id):
    with Session(db.engine) as session:
        with session.begin():
            query = select(CustomerAccount).filter(CustomerAccount.account_id == account_id)
            result = session.execute(query).scalars().first()
            
            if result is None:
                return jsonify({"error": "Customer account not found"}), 404
            
            account = result
            try:
                account_data = customer_account_schema.load(request.json)
            except ValidationError as err:
                return jsonify(err.messages), 400
            
            for field, value in account_data.items():
                setattr(account, field, value)
                
            session.commit()
            return jsonify({"message": "Customer account details successfully updated!"}), 200
 
        
@app.route("/customer_accounts/<int:account_id>", methods=["DELETE"])
def delete_customer_account(account_id):
    with Session(db.engine) as session:
        with session.begin():
            query = select(CustomerAccount).filter(CustomerAccount.account_id == account_id)
            customer_account = session.execute(query).scalars().first()
            
            if customer_account is None:
                return jsonify ({"error": "Customer account not found"}), 404

            customer_id = customer_account.customer_id
            orders_query = select(Order).filter(Order.customer_id == customer_id)
            orders = session.execute(orders_query).scalars().all()
            
            if orders:
                return jsonify({"error": "Cannot delete customer accounts with associated existing orders"}), 400
            
            delete_statement = delete(CustomerAccount).where(CustomerAccount.account_id == account_id)
            session.execute(delete_statement)
            session.commit()
            
            return jsonify({"message": "Customer account was deleted successfully."}), 200

    
             



    






if __name__ == "__main__":
    app.run(debug=True)