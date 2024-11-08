import streamlit as st
import mysql.connector
import pandas as pd
import hashlib

# Database connection configuration
db_config = {
    'host': 'localhost',
    'user': 'root',  # Replace with your MySQL username
    'password': 'Smit@1963',  # Replace with your MySQL password
    'database': 'ecommerce_db'
}


# Utility function for password hashing
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


# Database connection function
def get_connection():
    return mysql.connector.connect(**db_config)


# User registration
def register_user(username, email, password):
    hashed_pw = hash_password(password)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)",
                       (username, email, hashed_pw))
        conn.commit()
        st.success("User registered successfully!")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()


# User login
def login_user(username, password):
    hashed_pw = hash_password(password)
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, hashed_pw))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user


# Fetch products from the database
def get_products():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    return products


# Place an order
def place_order(user_id, product_id, quantity):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO orders (user_id, product_id, quantity) VALUES (%s, %s, %s)",
                       (user_id, product_id, quantity))
        conn.commit()
        st.success("Order placed successfully!")
    except mysql.connector.Error as err:
        st.error(f"Error: {err}")
    finally:
        cursor.close()
        conn.close()


# Streamlit app layout
st.title("E-commerce Web App")

# Sidebar for user authentication
st.sidebar.header("User Authentication")
auth_choice = st.sidebar.radio("Choose an option:", ["Register", "Login"])

if auth_choice == "Register":
    st.sidebar.subheader("Create an Account")
    reg_username = st.sidebar.text_input("Username")
    reg_email = st.sidebar.text_input("Email")
    reg_password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Register"):
        register_user(reg_username, reg_email, reg_password)

elif auth_choice == "Login":
    st.sidebar.subheader("Login to Your Account")
    login_username = st.sidebar.text_input("Username")
    login_password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        user = login_user(login_username, login_password)
        if user:
            st.session_state["user"] = user
            st.success(f"Welcome, {user['username']}!")
        else:
            st.error("Invalid username or password.")

# Main section - product listing and order placement
if "user" in st.session_state:
    st.header("Available Products")
    products = get_products()
    product_df = pd.DataFrame(products)
    st.write(product_df[["product_name", "description", "price", "stock_units", "rating"]])

    # Order placement
    st.subheader("Place an Order")
    selected_product = st.selectbox("Select a product to order:", product_df["product_name"].tolist())
    quantity = st.number_input("Quantity", min_value=1, max_value=100, step=1)

    # Get product ID from the selected product name
    product_id = product_df.loc[product_df["product_name"] == selected_product, "id"].values[0]

    if st.button("Place Order"):
        place_order(st.session_state["user"]["id"], product_id, quantity)
else:
    st.write("Please log in to view products and place an order.")
