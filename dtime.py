# discount_marketplace.py
import streamlit as st
import sqlite3
import uuid

# Set up the Streamlit page (must be the first command)
st.set_page_config(layout="wide")  # Use the full width of the screen

# Hide Streamlit menu, footer, and prevent code inspection
st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .stDeployButton {display: none !important;}  /* Hide GitHub button */
    </style>

    <script>
    document.addEventListener('contextmenu', event => event.preventDefault());
    document.onkeydown = function(e) {
        if (e.ctrlKey && (e.keyCode === 85 || e.keyCode === 83)) {
            return false;  // Disable "Ctrl + U" (View Source) & "Ctrl + S" (Save As)
        }
        if (e.keyCode == 123) {
            return false;  // Disable "F12" (DevTools)
        }
    };
    </script>
    """, unsafe_allow_html=True)

# Custom CSS for better styling
st.markdown(
    """
    <style>
    /* General Styling */
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f5f5f5;
    }
    @keyframes slide {
        0% { transform: translateX(0%); }
        100% { transform: translateX(-100%); }
    }
    /* Popup CSS */
    .popup {
        position: fixed;
        top: 20px;
        right: 20px;
        background-color: #4CAF50;
        color: white;
        padding: 15px;
        border-radius: 5px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        z-index: 1000;
        animation: fadeInOut 3s ease-in-out;
    }
    @keyframes fadeInOut {
        0% { opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { opacity: 0; }
    }
    /* Image Container */
    .image-container {
        width: 100px;
        height: 100px;
        border-radius: 8px;
        overflow: hidden;
        border: 2px solid #e0e0e0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        margin-right: 15px;
    }

    .image-container img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.3s ease;
    }

    .image-container img:hover {
        transform: scale(1.05);
    }

    .shop-name {
        font-size: 1em; /* Adjust the font size as needed */
        color: #333; /* Change color if needed */
        overflow: hidden; /* Hide overflow if the text is too long */
        text-overflow: ellipsis; /* Add ellipsis for overflow text */
        white-space: nowrap; /* Prevent text from wrapping */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Custom CSS for Shop Dashboard
shop_dashboard_css = """
<style>
    /* Main Container */
    .dashboard-container {
        padding: 20px;
        background: #f8f9fa;
    }

    /* Add New Discount Form */
    .discount-form {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 30px;
    }

    /* Product Image Preview */
    .image-preview {
        width: 200px;
        height: 200px;
        border-radius: 12px;
        overflow: hidden;
        margin: 15px auto;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border: 3px solid #ffffff;
        position: relative;
        background: #ffffff;
    }

    .image-preview img {
        width: 100%;
        height: 100%;
        object-fit: contain;
        transition: transform 0.3s ease;
    }

    .image-preview:hover img {
        transform: scale(1.05);
    }

    /* Discount Card */
    .discount-card {
        background: white;
        border-radius: 15px;
        padding: 20px;
        margin: 15px 0;
        display: flex;
        align-items: center;
        gap: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        border: 1px solid #e0e0e0;
    }

    .discount-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
    }

    /* Product Image in Card */
    .product-image {
        width: 150px;
        height: 150px;
        border-radius: 10px;
        overflow: hidden;
        flex-shrink: 0;
        border: 2px solid #f0f0f0;
    }

    .product-image img {
        width: 100%;
        height: 100%;
        object-fit: cover;
        transition: transform 0.3s ease;
    }

    .product-image:hover img {
        transform: scale(1.1);
    }

    /* Discount Details */
    .discount-details {
        flex-grow: 1;
    }

    .product-title {
        font-size: 1.4em;
        font-weight: 600;
        color: #2c3e50;
        margin-bottom: 10px;
    }

    .discount-rate {
        display: inline-block;
        background: #ff4757;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 500;
        margin: 5px 0;
    }

    .coupon-container {
        background: #f8f9fa;
        padding: 8px 15px;
        border-radius: 8px;
        margin: 10px 0;
        display: inline-block;
    }

    .coupon-code {
        font-family: 'Courier New', monospace;
        font-size: 1.1em;
        color: #2c3e50;
        font-weight: 600;
        letter-spacing: 1px;
    }

    .availability {
        color: #666;
        font-size: 0.9em;
        margin-top: 5px;
    }

    /* Controls */
    .controls {
        display: flex;
        gap: 10px;
        margin-top: 15px;
    }

    .toggle-button {
        background: #4CAF50;
        color: white;
        padding: 8px 15px;
        border-radius: 6px;
        border: none;
        cursor: pointer;
        transition: background 0.3s ease;
    }

    .toggle-button:hover {
        background: #43A047;
    }

    .delete-button {
        background: #ff4757;
        color: white;
        padding: 8px 15px;
        border-radius: 6px;
        border: none;
        cursor: pointer;
        transition: background 0.3s ease;
    }

    .delete-button:hover {
        background: #ff3748;
    }

    /* Form Inputs */
    .input-group {
        margin-bottom: 20px;
    }

    .input-label {
        display: block;
        margin-bottom: 8px;
        color: #2c3e50;
        font-weight: 500;
    }

    .input-field {
        width: 100%;
        padding: 10px;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        transition: border-color 0.3s ease;
    }

    .input-field:focus {
        border-color: #2962ff;
        outline: none;
    }

    /* Add Discount Button */
    .add-button {
        background: #2962ff;
        color: white;
        padding: 12px 25px;
        border-radius: 8px;
        border: none;
        cursor: pointer;
        font-weight: 500;
        transition: all 0.3s ease;
    }

    .add-button:hover {
        background: #1e88e5;
        transform: translateY(-2px);
    }
</style>
"""

# -------------------- Database Setup -------------------- #
conn = sqlite3.connect('marketplace.db', check_same_thread=False)
c = conn.cursor()

# Create shops table
c.execute('''
CREATE TABLE IF NOT EXISTS shops (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    shop_name TEXT,
    logo_url TEXT,
    gst_number TEXT,
    category TEXT,
    custom_category_image TEXT,
    location TEXT,
    contact_number TEXT
)
''')

# Create customers table
c.execute('''
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT,
    full_name TEXT,
    profile_image TEXT,
    contact_number TEXT,
    location TEXT
)
''')

# Create discounts table
c.execute('''
CREATE TABLE IF NOT EXISTS discounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    shop_id INTEGER,
    product_name TEXT,
    product_image TEXT,
    discount_rate TEXT,
    is_active INTEGER DEFAULT 1,
    coupon_code TEXT,
    available_for_first INTEGER DEFAULT 0,
    FOREIGN KEY (shop_id) REFERENCES shops(id)
)
''')

# Create categories table
c.execute('''
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE,
    image_url TEXT
)
''')

conn.commit()

# -------------------- Helper Functions -------------------- #
def register_shop(data):
    try:
        c.execute('''INSERT INTO shops (username, password, shop_name, logo_url, gst_number, category, custom_category_image, location, contact_number)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''', data)
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def register_customer(data):
    try:
        c.execute('''INSERT INTO customers (username, password, full_name, profile_image, contact_number, location)
                     VALUES (?, ?, ?, ?, ?, ?)''', data)
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(role, username, password):
    table = 'shops' if role == 'shop' else 'customers'
    c.execute(f"SELECT * FROM {table} WHERE username=? AND password=?", (username, password))
    return c.fetchone()

def get_shop_details(shop_id):
    c.execute("SELECT * FROM shops WHERE id=?", (shop_id,))
    return c.fetchone()

def generate_coupon():
    return str(uuid.uuid4())[:8]

# -------------------- Admin Functions -------------------- #
def get_all_shops():
    c.execute("SELECT * FROM shops")
    return c.fetchall()

def get_all_customers():
    c.execute("SELECT id, username, password, full_name, profile_image, contact_number, location FROM customers")
    return c.fetchall()

def get_all_discounts():
    c.execute("SELECT * FROM discounts")
    return c.fetchall()

def delete_shop(shop_id):
    c.execute("DELETE FROM shops WHERE id=?", (shop_id,))
    conn.commit()

def delete_customer(customer_id):
    c.execute("DELETE FROM customers WHERE id=?", (customer_id,))
    conn.commit()

def delete_discount(discount_id):
    c.execute("DELETE FROM discounts WHERE id=?", (discount_id,))
    conn.commit()

# Function to get all categories
def get_all_categories():
    c.execute("SELECT id, name, image_url FROM categories")  # Adjust the query based on your categories table structure
    return c.fetchall()

# Function to update category details
def update_category(category_id, new_name, new_image):
    c.execute("UPDATE categories SET name=?, image_url=? WHERE id=?", (new_name, new_image, category_id))
    conn.commit()

# Function to add a new category
def add_category(name, image_url):
    c.execute("INSERT INTO categories (name, image_url) VALUES (?, ?)", (name, image_url))
    conn.commit()

# Function to fetch categories for registration with images
def fetch_categories():
    c.execute("SELECT name, image_url FROM categories")
    return c.fetchall()  # Returns a list of tuples (name, image_url)

# Function to check if a URL is a valid image URL
def is_valid_image_url(url):
    # Check if the URL ends with a valid image extension
    return url.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp')) or "lh3.googleusercontent.com" in url

# -------------------- UI Components -------------------- #
st.title("Local Discount Marketplace")

menu = ["Home", "Register", "Login", "Admin Login"]
if 'user' in st.session_state:
    if st.session_state['role'] == 'shop':
        menu = ["Shop Dashboard"]
    elif st.session_state['role'] == 'customer':
        menu = ["Customer Dashboard"]
    elif st.session_state['role'] == 'admin':
        menu = ["Admin Dashboard"]

choice = st.sidebar.selectbox("Menu", menu)

if choice == "Register":
    role = st.radio("Register as", ["Shop", "Customer"])
    if role == "Shop":
        st.subheader("Shop Registration")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        shop_name = st.text_input("Shop Name")
        logo_url = st.text_input("Shop Logo URL (PNG)")
        gst_number = st.text_input("GST Number")
        
        # Fetch categories from the database
        categories = fetch_categories()
        if categories:
            category_names = [cat[0] for cat in categories]  # Extract names for the selectbox
            category = st.selectbox("Category", category_names)  # Use fetched category names
        else:
            st.error("No categories available. Please add categories in the admin section.")
        
        custom_image = ""
        if category == "Other":
            custom_image = st.text_input("Image URL for Custom Category")
        location = st.text_input("Shop Location")
        contact_number = st.text_input("Contact Number")
        if st.button("Register Shop"):
            data = (username, password, shop_name, logo_url, gst_number, category, custom_image, location, contact_number)
            if register_shop(data):
                st.success("Shop registered successfully!")
            else:
                st.error("Username already exists.")
    else:
        st.subheader("Customer Registration")
        username = st.text_input("Username")
        password = st.text_input("Password", type='password')
        full_name = st.text_input("Full Name")
        profile_image = st.text_input("Profile Image URL")
        contact_number = st.text_input("Contact Number")
        location = st.text_input("Location")
        if st.button("Register Customer"):
            data = (username, password, full_name, profile_image, contact_number, location)
            if register_customer(data):
                st.success("Customer registered successfully!")
            else:
                st.error("Username already exists.")

elif choice == "Login":
    role = st.radio("Login as", ["Shop", "Customer"])
    st.subheader(f"{role} Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    if st.button("Login"):
        user = login_user(role.lower(), username, password)
        if user:
            st.success(f"Welcome, {username}!")
            st.session_state['user'] = user
            st.session_state['role'] = role.lower()
            st.rerun()
        else:
            st.error("Invalid credentials")

elif choice == "Admin Login":
    st.subheader("Admin Login")
    admin_username = st.text_input("Admin Username")
    admin_password = st.text_input("Admin Password", type='password')
    
    if st.button("Login as Admin"):
        if admin_username == "admin" and admin_password == "admin":  # Simple authentication
            st.session_state['user'] = admin_username  # Set admin username in session state
            st.session_state['role'] = 'admin'  # Set role to admin
            st.success("Welcome Admin!")
            st.rerun()  # Rerun to update the sidebar menu

        else:
            st.error("Invalid admin credentials")

elif choice == "Shop Dashboard" and st.session_state.get('role') == 'shop':
    shop = st.session_state['user']
    st.subheader(f"Welcome, {shop[3]}!")
    st.write("Here you will manage your discount listings.")

    # Add New Discount Form
    st.markdown("### Add New Discount or Product")
    
    # Use Streamlit form to handle submission
    with st.form(key='add_discount_form'):
        product_name = st.text_input("Product Name")
        product_image = st.text_input("Product Image URL (PNG)")
        
        # Show image preview
        if product_image:
            st.image(product_image, caption="Product preview", width=200)
            
        discount_rate = st.text_input("Discount Rate (e.g., 20%)")
        available_for_first = st.number_input("Available for First (No. of People)", min_value=0, value=0)
        
        # Submit button
        submit_button = st.form_submit_button("Add Discount")
        
        if submit_button:
            coupon = generate_coupon()
            # Prepare values for database insertion
            available_for_first_value = available_for_first if available_for_first > 0 else None
            
            # Insert into the database, allowing for None values
            c.execute('''INSERT INTO discounts (shop_id, product_name, product_image, discount_rate, coupon_code, available_for_first) 
                         VALUES (?, ?, ?, ?, ?, ?)''', 
                         (shop[0], product_name or None, product_image or None, discount_rate or None, coupon, available_for_first_value))
            conn.commit()
            st.success("Discount added successfully!")
            st.rerun()

    # Listed Discounts
    st.markdown("### Your Listed Discounts")
    c.execute("SELECT * FROM discounts WHERE shop_id=?", (shop[0],))
    rows = c.fetchall()
    
    for row in rows:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col1:
            if row[3]:  # Product image
                st.image(row[3], width=100)
            else:
                logo_url = shop[4] if shop[4] and is_valid_image_url(shop[4]) else "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/2048px-No_image_available.svg.png"
                st.image(logo_url, width=100)  # Display shop logo or fallback image
        
        with col2:
            if row[2]:  # Product name
                st.markdown(f"**{row[2]}**")
            st.markdown(f"**{row[4]} OFF**")
            st.markdown(f"Coupon Code: `{row[6]}`")
            available_text = "Available for First: " + str(row[7]) + " People" if row[7] else "Available for All"
            st.markdown(available_text)
        
        with col3:
            # Create unique keys for each button
            toggle_key = f"toggle_{row[0]}"
            delete_key = f"delete_{row[0]}"
            
            # Active/Inactive toggle
            is_active = bool(row[5])
            if st.checkbox("Active", value=is_active, key=toggle_key):
                if not is_active:
                    c.execute("UPDATE discounts SET is_active=1 WHERE id=?", (row[0],))
                    conn.commit()
                    st.rerun()
            else:
                if is_active:
                    c.execute("UPDATE discounts SET is_active=0 WHERE id=?", (row[0],))
                    conn.commit()
                    st.rerun()
            
            # Delete button
            if st.button("Delete", key=delete_key):
                c.execute("DELETE FROM discounts WHERE id=?", (row[0],))
                conn.commit()
                st.success(f"Deleted discount for: {row[2] if row[2] else 'product'}")
                st.rerun()

            # Google Maps link for shop name and location
            st.markdown(f'''
                <div class="shop-name">
                    <a href="https://www.google.com/maps/search/?api=1&query={row[4]} {row[6]}" target="_blank">
                        {row[4]}
                    </a>
                </div>
            ''', unsafe_allow_html=True)

elif choice == "Customer Dashboard" and st.session_state.get('role') == 'customer':
    customer = st.session_state['user']
    if customer[4]:  # Assuming customer[4] is the profile image URL
        st.sidebar.image(customer[4], width=150)  # Display customer profile image
    else:
        st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/2048px-No_image_available.svg.png", width=150)  # Fallback to a default image
    st.sidebar.markdown(f"**{customer[3]}**")
    st.sidebar.markdown(f"**Contact:** {customer[5]}")
    st.sidebar.markdown(f"**Location:** {customer[6]}")

    st.subheader(f"Welcome, {customer[3]}!")

    # Fetch categories for customer dashboard
    categories = fetch_categories()
    if categories:
        # Create tabs for each category plus an "All" tab
        tab_names = ["All"] + [cat[0] for cat in categories]  # Add "All" tab
        tabs = st.tabs(tab_names)  # Create tabs

        # All tab
        with tabs[0]:  # First tab for "All"
            st.subheader("All Discounts")
            search_query = st.text_input("Search by Product Name, Location, or Shop Name")
            
            # Fetch all products including location
            c.execute("""
                SELECT d.product_name, d.product_image, d.discount_rate, d.coupon_code, s.shop_name, s.logo_url, s.location, d.available_for_first 
                FROM discounts d 
                JOIN shops s ON d.shop_id = s.id 
                WHERE d.is_active = 1
            """)
            all_items = c.fetchall()

            # Filter items based on search query
            if search_query:
                all_items = [
                    item for item in all_items 
                    if (search_query.lower() in (item[0] or "").lower() or  # Product Name
                        search_query.lower() in (item[6] or "").lower() or  # Location
                        search_query.lower() in (item[4] or "").lower())    # Shop Name
                ]

            if all_items:
                all_items.reverse()  # Reverse the order of items
                for i in range(0, len(all_items), 5):
                    cols = st.columns(5)
                    for j, item in enumerate(all_items[i:i+5]):
                        with cols[j]:
                            # Create a container for each product
                            st.markdown(f'''
                                <div class="product-box">
                                    <div class="image-container">
                                        <img src="{item[1] if item[1] else item[5]}" alt="Product Image">
                                    </div>
                                    <div class="product-details">
                                        <div class="product-name">{item[0] if item[0] else item[4]}</div>
                                        <div class="discount-tag">Discount: {item[2]}</div>
                                        <div>Coupon: <span class="coupon-code">{item[3]}</span></div>
                                        <div class="shop-name">
                                            <a href="https://www.google.com/maps/search/?api=1&query={item[4]} {item[6]}" target="_blank">
                                                {item[4]} - {item[6]}
                                            </a>
                                        </div>
                                        <div>Available for: {item[7] if item[7] is not None else "All"}</div>
                                    </div>
                                </div>
                            ''', unsafe_allow_html=True)
            else:
                st.info("No active discounts found.")

        # Existing category tabs
        for index, category in enumerate(categories):
            category_name, category_image = category  # Unpack the category tuple
            with tabs[index + 1]:  # Use the corresponding tab
                st.markdown(f'''
                    <div class="category-box">
                        <img src="{category_image}" width="100"><br>{category_name}
                    </div>
                ''', unsafe_allow_html=True)

                # Fetch products for the selected category
                c.execute("""
                    SELECT d.product_name, d.product_image, d.discount_rate, d.coupon_code, s.shop_name, s.logo_url, d.available_for_first 
                    FROM discounts d 
                    JOIN shops s ON d.shop_id = s.id 
                    WHERE s.category = ? AND d.is_active = 1
                """, (category_name,))
                items = c.fetchall()

                if items:
                    items.reverse()  # Reverse the order of items
                    for i in range(0, len(items), 5):
                        cols = st.columns(5)
                        for j, item in enumerate(items[i:i+5]):
                            with cols[j]:
                                # Create a container for each product
                                st.markdown(f'''
                                    <div class="product-box">
                                        <div class="image-container">
                                            <a href="{item[1]}" target="_blank">
                                                <img src="{item[1] if item[1] else item[5]}" alt="Product Image">
                                            </a>
                                        </div>
                                        <div class="product-details">
                                            <div class="product-name">{item[0] if item[0] else item[4]}</div>
                                            <div class="discount-tag">Discount: {item[2]}</div>
                                            <div>Coupon: <span class="coupon-code">{item[3]}</span></div>
                                            <div class="shop-name">
                                                <a href="https://www.google.com/maps/search/?api=1&query={item[4]} {customer[6]}" target="_blank">
                                                    {item[4]} - {customer[6]}
                                                </a>
                                            </div>
                                            <div>Available for: {item[6] if item[6] is not None else "All"}</div>
                                        </div>
                                    </div>
                                ''', unsafe_allow_html=True)
                else:
                    st.info("No active discounts in this category.")
    else:
        st.error("No categories available. Please add categories in the admin section.")

elif choice == "Admin Dashboard":
    if st.session_state.get('role') != 'admin':
        st.error("You must be logged in as an admin to access this page.")
    else:
        st.subheader("Admin Dashboard")
        
        # Custom CSS for Admin Dashboard
        admin_dashboard_css = """
        <style>
            /* Admin Dashboard Container */
            .admin-section {
                background: white;
                border-radius: 10px;
                padding: 20px;
                margin: 15px 0;
                box-shadow: 0 2px 12px rgba(0,0,0,0.1);
            }

            /* Section Headers */
            .section-header {
                color: #1a237e;
                font-size: 24px;
                font-weight: 600;
                padding-bottom: 10px;
                border-bottom: 2px solid #1a237e;
                margin-bottom: 20px;
            }

            /* Card Layout */
            .admin-card {
                background: #ffffff;
                border-radius: 8px;
                padding: 15px;
                margin: 10px 0;
                border: 1px solid #e0e0e0;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                gap: 20px;
            }

            .admin-card:hover {
                box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                transform: translateY(-2px);
            }

            /* Image Container */
            .image-container {
                width: 100px;
                height: 100px;
                border-radius: 8px;
                overflow: hidden;
                border: 2px solid #e0e0e0;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
                margin-right: 15px;
            }

            .image-container img {
                width: 100%;
                height: 100%;
                object-fit: cover;
                transition: transform 0.3s ease;
            }

            .image-container img:hover {
                transform: scale(1.05);
            }

            /* Content Layout */
            .content-container {
                flex-grow: 1;
            }

            .info-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 10px;
            }

            .info-item {
                margin: 5px 0;
            }

            .info-label {
                color: #666;
                font-size: 0.9em;
                font-weight: 500;
            }

            .info-value {
                color: #333;
                font-weight: 600;
            }

            /* Action Buttons */
            .action-container {
                display: flex;
                gap: 10px;
                margin-top: 10px;
            }

            .action-button {
                padding: 6px 12px;
                border-radius: 4px;
                border: none;
                cursor: pointer;
                font-weight: 500;
                transition: all 0.2s ease;
            }

            .delete-button {
                background-color: #ff1744;
                color: white;
            }

            .delete-button:hover {
                background-color: #d50000;
            }

            .edit-button {
                background-color: #2962ff;
                color: white;
            }

            .edit-button:hover {
                background-color: #0039cb;
            }

            /* Category Pills */
            .category-pill {
                display: inline-block;
                padding: 4px 12px;
                border-radius: 20px;
                background-color: #e3f2fd;
                color: #1565c0;
                font-size: 0.9em;
                margin: 4px;
            }

            /* Discount Badge */
            .discount-badge {
                background-color: #ff4757;
                color: white;
                padding: 4px 8px;
                border-radius: 4px;
                font-weight: 500;
                display: inline-block;
                margin: 4px 0;
            }

            /* Coupon Code */
            .coupon-code {
                font-family: monospace;
                background-color: #f5f5f5;
                padding: 4px 8px;
                border-radius: 4px;
                color: #333;
                font-size: 0.9em;
            }

            /* Add New Button */
            .add-new-button {
                background-color: #00c853;
                color: white;
                padding: 10px 20px;
                border-radius: 6px;
                border: none;
                cursor: pointer;
                font-weight: 500;
                display: inline-flex;
                align-items: center;
                gap: 8px;
                margin: 20px 0;
                transition: all 0.2s ease;
            }

            .add-new-button:hover {
                background-color: #00a844;
                transform: translateY(-2px);
            }

            /* Form Inputs */
            .admin-input {
                width: 100%;
                padding: 8px 12px;
                border: 1px solid #e0e0e0;
                border-radius: 4px;
                margin: 5px 0;
                transition: border-color 0.2s ease;
            }

            .admin-input:focus {
                border-color: #2962ff;
                outline: none;
            }

            /* Status Indicators */
            .status-active {
                color: #00c853;
                font-weight: 500;
            }

            .status-inactive {
                color: #ff1744;
                font-weight: 500;
            }

            /* Responsive Design */
            @media (max-width: 768px) {
                .info-grid {
                    grid-template-columns: 1fr;
                }
                
                .admin-card {
                    flex-direction: column;
                    text-align: center;
                }
                
                .action-container {
                    justify-content: center;
                }
            }
        </style>
        """

        # Update the sections with new HTML structure
        def display_shop_card(shop):
            col1, col2, col3 = st.columns([1, 2, 1])
            with col1:
                # Check if the shop logo URL is valid before displaying it
                logo_url = shop[4] if shop[4] and is_valid_image_url(shop[4]) else "https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/2048px-No_image_available.svg.png"
                print("Image URL:", logo_url)  # Debugging line
                st.image(logo_url, width=100)  # Display shop logo or fallback image
            with col2:
                st.markdown(f"**Shop Name:** {shop[3]}")
                st.markdown(f"**Username:** {shop[1]}")
                st.markdown(f"**GST Number:** {shop[5]}")
                st.markdown(f"**Location:** {shop[8]}")
            with col3:
                if st.button("Edit", key=f"edit_shop_{shop[0]}"):
                    # Implement edit functionality here
                    # You can use st.text_input to allow the admin to change details
                    new_shop_name = st.text_input("New Shop Name", value=shop[3])
                    new_logo_url = st.text_input("New Logo URL", value=shop[4])
                    if st.button("Update"):
                        # Update the shop details in the database
                        c.execute("UPDATE shops SET shop_name=?, logo_url=? WHERE id=?", (new_shop_name, new_logo_url, shop[0]))
                        conn.commit()
                        st.success("Shop details updated successfully!")
                        st.rerun()

                if st.button("Delete", key=f"delete_shop_{shop[0]}"):
                    c.execute("DELETE FROM shops WHERE id=?", (shop[0],))
                    conn.commit()
                    st.success(f"Deleted shop: {shop[3]}")
                    st.rerun()

        # Add the CSS to your Streamlit app
        st.markdown(admin_dashboard_css, unsafe_allow_html=True)

        # Create tabs for managing different sections
        tabs = st.tabs(["Manage Shops", "Manage Customers", "Manage Discounts", "Manage Categories", "Add New Category", "Change Shop Password"])

        # Manage Shops Tab
        with tabs[0]:
            st.markdown("### Manage Shops", unsafe_allow_html=True)
            
            # Searchable Dropdown for Shops
            search_query = st.text_input("Search for a shop")
            shops = get_all_shops()
            filtered_shops = [shop for shop in shops if search_query.lower() in shop[3].lower()]

            for shop in filtered_shops:
                display_shop_card(shop)

        # Manage Customers Tab
        with tabs[1]:
            st.markdown("### Manage Customers")
            search_query = st.text_input("Search for a customer")
            customers = get_all_customers()
            
            # Filter customers based on search query
            filtered_customers = [customer for customer in customers if search_query.lower() in customer[3].lower() or search_query.lower() in customer[1].lower()]

            for customer in filtered_customers:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    if customer[4]:  # Assuming customer[4] is the profile image URL
                        st.image(customer[4], width=100)  # Display customer profile image
                    else:
                        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/2048px-No_image_available.svg.png", width=100)  # Fallback to a default image
                with col2:
                    st.markdown(f"**Customer Name:** {customer[3]}")
                    st.markdown(f"**Username:** {customer[1]}")
                    st.markdown(f"**Contact Number:** {customer[5]}")
                    st.markdown(f"**Location:** {customer[6]}")
                with col3:
                    if st.button(f"Delete {customer[3]}", key=f"delete_customer_{customer[0]}"):
                        delete_customer(customer[0])
                        st.success(f"Deleted customer: {customer[3]}")
                        st.rerun()

        # Manage Discounts Tab
        with tabs[2]:
            st.markdown("### Manage Discounts")
            search_query = st.text_input("Search for a discount", "")
            discounts = get_all_discounts()
            
            # Filter discounts based on search query
            filtered_discounts = []
            if search_query:
                for discount in discounts:
                    shop_details = get_shop_details(discount[1])
                    product_name = discount[2] if discount[2] else (shop_details[3] if shop_details else "")
                    shop_name = shop_details[3] if shop_details else ""
                    
                    if (product_name and search_query.lower() in product_name.lower()) or \
                       (shop_name and search_query.lower() in shop_name.lower()):
                        filtered_discounts.append((discount, shop_details))
            else:
                filtered_discounts = [(discount, get_shop_details(discount[1])) for discount in discounts]

            for discount, shop_details in filtered_discounts:
                col1, col2, col3 = st.columns([1, 2, 1])
                with col1:
                    if discount[3]:
                        st.image(discount[3], width=100)
                    elif shop_details and shop_details[4]:
                        st.image(shop_details[4], width=100)
                    else:
                        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/a/ac/No_image_available.svg/2048px-No_image_available.svg.png", width=100)
                with col2:
                    product_name = discount[2] if discount[2] else f"Product by {shop_details[3]}" if shop_details else "Unknown Product"
                    shop_name = shop_details[3] if shop_details else "Unknown Shop"
                    
                    st.markdown(f'''
                        <div class="flex-container">
                            <div>
                                <div class="product-name">{product_name}</div>
                                <div>Discount: {discount[4]}</div>
                                <div>Coupon: <code>{discount[6]}</code></div>
                                <div class="shop-name">Shop: {shop_name}</div>
                            </div>
                        </div>
                    ''', unsafe_allow_html=True)
                with col3:
                    if st.button(f"Delete Discount", key=f"delete_discount_{discount[0]}"):
                        delete_discount(discount[0])
                        st.success(f"Deleted discount for: {product_name}")
                        st.rerun()

        # Manage Categories Tab
        with tabs[3]:
            st.markdown("### Manage Categories")
            search_query = st.text_input("Search for a category")
            categories = get_all_categories()  # Fetch all categories
            
            # Filter categories based on search query
            filtered_categories = [category for category in categories if search_query.lower() in category[1].lower()]

            if filtered_categories:
                for category in filtered_categories:
                    col1, col2, col3 = st.columns([1, 2, 1])
                    with col1:
                        st.image(category[2], width=100)  # Display category image
                    with col2:
                        st.markdown(f"**Category Name:** {category[1]}")
                    with col3:
                        if st.button(f"Edit {category[1]}", key=f"edit_category_{category[0]}"):
                            # Prepare to edit the selected category
                            new_name = st.text_input("New Category Name", value=category[1])
                            new_image = st.text_input("New Image URL", value=category[2])
                            if st.button("Update Category", key=f"update_category_{category[0]}"):
                                update_category(category[0], new_name, new_image)
                                st.success("Category updated successfully!")
                                st.rerun()  # Rerun to refresh the page
            else:
                st.info("No categories found.")

        # Add New Category Tab
        with tabs[4]:
            st.markdown("### Add New Category")
            new_category_name = st.text_input("New Category Name")
            new_category_image = st.text_input("New Image URL")
            if st.button("Add Category"):
                if new_category_name and new_category_image:
                    add_category(new_category_name, new_category_image)
                    st.success("Category added successfully!")
                    st.rerun()  # Rerun to refresh the page
                else:
                    st.error("Please provide both category name and image URL.")

        # Change Shop Password Tab
        with tabs[5]:
            st.markdown("### Change Shop Password")
            shop_id = st.selectbox("Select Shop", [shop[0] for shop in shops], format_func=lambda x: next(shop[3] for shop in shops if shop[0] == x))
            new_password = st.text_input("New Password", type='password')
            if st.button("Change Password"):
                c.execute("UPDATE shops SET password=? WHERE id=?", (new_password, shop_id))
                conn.commit()
                st.success("Password changed successfully!")

elif choice == "Home":
    st.info("Register or Login from sidebar to explore the discount marketplace.")

# Custom CSS for styling
custom_css = """
<style>
    /* General Styles */
    body {
        font-family: 'Arial', sans-serif;
        background-color: #f5f5f5; /* Light background for better contrast */
    }

    /* Product Box Container */
    .product-box {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 15px;
        margin: 10px;
        background-color: white;
        height: auto; /* Allow height to adjust based on content */
        display: flex;
        flex-direction: column;
        justify-content: center; /* Center content vertically */
        align-items: center; /* Center content horizontally */
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .product-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }

    /* Image Container */
    .image-container {
        display: flex;
        justify-content: center; /* Center horizontally */
        align-items: center; /* Center vertically */
        width: 100%; /* Ensure it takes full width */
        height: 150px; /* Set a fixed height for the image container */
        overflow: hidden; /* Hide overflow */
        padding: 10px; /* Add padding to the image container */
    }

    .image-container img {
        max-width: 100%; /* Ensure the image does not exceed the container width */
        max-height: 100%; /* Ensure the image does not exceed the container height */
        object-fit: cover; /* Maintain aspect ratio */
        border-radius: 8px; /* Rounded corners for images */
    }

    /* Shop Logo */
    .shop-logo {
        width: 80px;
        height: 80px;
        object-fit: cover;
        border-radius: 50%;
        border: 3px solid white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    /* Product Details */
    .product-details {
        width: 100%;
        text-align: center;
    }

    .product-name {
        font-weight: 600;
        font-size: 1.2em; /* Slightly larger font size */
        color: #333;
        margin: 8px 0;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    .discount-tag {
        background-color: #ff4757;
        color: white;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 0.9em;
        font-weight: 500;
        margin: 5px 0;
    }

    .coupon-code {
        background-color: #f1f2f6;
        padding: 10px;
        border-radius: 5px;
        font-family: monospace;
        font-size: 0.9em;
        color: #2f3542;
    }

    /* Shop Name */
    .shop-name {
        font-size: 0.9em; /* Smaller font size */
        color: #007bff; /* Blue color for better visibility */
        overflow: hidden; /* Hide overflow if the text is too long */
        text-overflow: ellipsis; /* Add ellipsis for overflow text */
        white-space: nowrap; /* Prevent text from wrapping */
        margin: 5px 0; /* Add margin for spacing */
        transition: color 0.3s ease; /* Smooth color transition */
    }

    .shop-name a {
        text-decoration: none; /* Remove underline from links */
    }

    .shop-name a:hover {
        color: #0056b3; /* Darker blue on hover */
    }

    /* Category Box */
    .category-box {
        border: 1px solid #e0e0e0;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        margin: 10px;
        transition: all 0.3s ease;
        cursor: pointer;
        background-color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }

    .category-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }

    .category-box img {
        width: 100px;
        height: 100px;
        object-fit: cover;
        border-radius: 8px;
        margin-bottom: 10px;
    }

    .discount-rate {
        background: #ff4757; /* Red background for discount */
        color: white;
        padding: 10px 15px; /* Increased padding for the discount badge */
        border-radius: 20px;
        font-weight: bold;
        margin: 10px 0; /* Add margin for spacing */
    }

    .coupon-code {
        font-family: 'Courier New', monospace;
        background: #f8f9fa; /* Light background for coupon code */
        padding: 10px; /* Increased padding */
        border-radius: 5px;
        margin: 5px 0; /* Add margin for spacing */
    }
</style>
"""

# Inject the CSS into the Streamlit app
st.markdown(custom_css, unsafe_allow_html=True)