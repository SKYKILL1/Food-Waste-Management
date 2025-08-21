import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="Food Wastage Management System",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database connection
def get_db_connection():
    conn = sqlite3.connect('food_wastage.db')
    conn.row_factory = sqlite3.Row
    return conn

# Initialize navigation
def main():
    st.sidebar.title("🍲 Navigation")
    
    # Navigation options
    nav_options = [
        "Project Introduction",
        "View Tables",
        "CRUD Operations",
        "SQL Queries & Visualization",
        "Learner SQL Queries",
    ]
    
    selected_nav = st.sidebar.radio("Go to", nav_options)
    
    # Display selected section
    if selected_nav == "Project Introduction":
        show_introduction()
    elif selected_nav == "View Tables":
        show_tables()
    elif selected_nav == "CRUD Operations":
        show_crud_operations()
    elif selected_nav == "SQL Queries & Visualization":
        show_queries_visualization()
    elif selected_nav == "Learner SQL Queries":
        show_learner_queries()


# Project Introduction
def show_introduction():
    st.title("🍲 Local Food Wastage Management System")
    
    st.markdown("""
    This project helps manage surplus food and reduce wastage by connecting providers with those in need.
    
    - **Providers:** Restaurants, households, and businesses list surplus food.  
    - **Receivers:** NGOs and individuals claim available food.  
    - **Geolocation:** Helps locate nearby food.  
    - **SQL Analysis:** Powerful insights using SQL queries.
    """)
    
    # Display some stats
    col1, col2, col3 = st.columns(3)
    
    with col1:
        conn = get_db_connection()
        total_food = pd.read_sql_query("SELECT COUNT(*) as count FROM food", conn)['count'][0]
        st.metric("Total Food Listings", total_food)
        conn.close()
    
    with col2:
        conn = get_db_connection()
        total_claims = pd.read_sql_query("SELECT COUNT(*) as count FROM claims", conn)['count'][0]
        st.metric("Total Claims", total_claims)
        conn.close()
    
    with col3:
        conn = get_db_connection()
        completed_claims = pd.read_sql_query(
            "SELECT COUNT(*) as count FROM claims WHERE Status = 'Completed'", conn
        )['count'][0]
        st.metric("Completed Claims", completed_claims)
        conn.close()
    
    # Show a map of providers (simplified)
    st.subheader("Provider Locations")
    conn = get_db_connection()
    providers = pd.read_sql_query("SELECT * FROM providers", conn)
    conn.close()
    
    if not providers.empty and 'City' in providers.columns:
        city_counts = providers['City'].value_counts().reset_index()
        city_counts.columns = ['City', 'Count']
        
        fig = px.bar(city_counts, x='City', y='Count', title='Providers by City')
        st.plotly_chart(fig, use_container_width=True)

# View Tables
def show_tables():
    st.title("📊 View Database Tables")
    
    table_options = ["providers", "food", "receivers", "claims"]
    selected_table = st.selectbox("Select a table to view", table_options)
    
    conn = get_db_connection()
    df = pd.read_sql_query(f"SELECT * FROM {selected_table}", conn)
    conn.close()
    
    st.dataframe(df, use_container_width=True)
    
    st.download_button(
        label="Download data as CSV",
        data=df.to_csv(index=False),
        file_name=f"{selected_table}.csv",
        mime="text/csv",
    )

# CRUD Operations
def show_crud_operations():
    st.title("🔄 CRUD Operations")
    
    crud_options = ["Add Record", "Update Record", "Delete Record"]
    selected_crud = st.radio("Select operation", crud_options)
    
    if selected_crud == "Add Record":
        st.subheader("Add New Record")
        
        table_options = ["providers", "food", "receivers", "claims"]
        selected_table = st.selectbox("Select table", table_options)
        
        if selected_table == "providers":
            st.write("Add a new provider")
            with st.form("add_provider"):
                name = st.text_input("Name")
                type_ = st.text_input("Type")
                address = st.text_input("Address")
                city = st.text_input("City")
                contact = st.text_input("Contact")
                
                submitted = st.form_submit_button("Add Provider")
                if submitted:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO providers (Name, Type, Address, City, Contact) VALUES (?, ?, ?, ?, ?)",
                        (name, type_, address, city, contact)
                    )
                    conn.commit()
                    conn.close()
                    st.success("Provider added successfully!")
        
        # Similar forms for other tables would go here
        
    elif selected_crud == "Update Record":
        st.subheader("Update Record")
        
        table_options = ["providers", "food", "receivers", "claims"]
        selected_table = st.selectbox("Select table to update", table_options)
        
        conn = get_db_connection()
        
        if selected_table == "providers":
            providers = pd.read_sql_query("SELECT * FROM providers", conn)
            selected_provider = st.selectbox("Select provider to update", providers['Provider_ID'])
            
            provider_data = pd.read_sql_query(
                f"SELECT * FROM providers WHERE Provider_ID = {selected_provider}", conn
            ).iloc[0]
            
            with st.form("update_provider"):
                name = st.text_input("Name", value=provider_data['Name'])
                type_ = st.text_input("Type", value=provider_data['Type'])
                address = st.text_input("Address", value=provider_data['Address'])
                city = st.text_input("City", value=provider_data['City'])
                contact = st.text_input("Contact", value=provider_data['Contact'])
                
                submitted = st.form_submit_button("Update Provider")
                if submitted:
                    cursor = conn.cursor()
                    cursor.execute(
                        """UPDATE providers SET Name = ?, Type = ?, Address = ?, 
                        City = ?, Contact = ? WHERE Provider_ID = ?""",
                        (name, type_, address, city, contact, selected_provider)
                    )
                    conn.commit()
                    st.success("Provider updated successfully!")
        
        elif selected_table == "food":
            food_items = pd.read_sql_query("SELECT * FROM food", conn)
            selected_food = st.selectbox("Select food item to update", food_items['Food_ID'])
            
            food_data = pd.read_sql_query(
                f"SELECT * FROM food WHERE Food_ID = {selected_food}", conn
            ).iloc[0]
            
            with st.form("update_food"):
                food_name = st.text_input("Food Name", value=food_data['Food_Name'])
                quantity = st.number_input("Quantity", min_value=1, value=int(food_data['Quantity']))
                expiry_date = st.date_input("Expiry Date", value=pd.to_datetime(food_data['Expiry_Date']))
                provider_id = st.number_input("Provider ID", min_value=1, value=int(food_data['Provider_ID']))
                provider_type = st.text_input("Provider Type", value=food_data['Provider_Type'])
                location = st.text_input("Location", value=food_data['Location'])
                food_type = st.selectbox("Food Type", ["Vegetarian", "Non-Vegetarian", "Vegan"], 
                                       index=["Vegetarian", "Non-Vegetarian", "Vegan"].index(food_data['Food_Type']))
                meal_type = st.selectbox("Meal Type", ["Breakfast", "Lunch", "Dinner", "Snacks"], 
                                       index=["Breakfast", "Lunch", "Dinner", "Snacks"].index(food_data['Meal_Type']))
                
                submitted = st.form_submit_button("Update Food")
                if submitted:
                    cursor = conn.cursor()
                    cursor.execute(
                        """UPDATE food SET Food_Name = ?, Quantity = ?, Expiry_Date = ?, 
                        Provider_ID = ?, Provider_Type = ?, Location = ?, Food_Type = ?, 
                        Meal_Type = ? WHERE Food_ID = ?""",
                        (food_name, quantity, expiry_date, provider_id, provider_type, 
                         location, food_type, meal_type, selected_food)
                    )
                    conn.commit()
                    st.success("Food item updated successfully!")
        
        elif selected_table == "receivers":
            receivers = pd.read_sql_query("SELECT * FROM receivers", conn)
            selected_receiver = st.selectbox("Select receiver to update", receivers['Receiver_ID'])
            
            receiver_data = pd.read_sql_query(
                f"SELECT * FROM receivers WHERE Receiver_ID = {selected_receiver}", conn
            ).iloc[0]
            
            with st.form("update_receiver"):
                name = st.text_input("Name", value=receiver_data['Name'])
                type_ = st.text_input("Type", value=receiver_data['Type'])
                city = st.text_input("City", value=receiver_data['City'])
                contact = st.text_input("Contact", value=receiver_data['Contact'])
                
                submitted = st.form_submit_button("Update Receiver")
                if submitted:
                    cursor = conn.cursor()
                    cursor.execute(
                        """UPDATE receivers SET Name = ?, Type = ?, City = ?, 
                        Contact = ? WHERE Receiver_ID = ?""",
                        (name, type_, city, contact, selected_receiver)
                    )
                    conn.commit()
                    st.success("Receiver updated successfully!")
        
        elif selected_table == "claims":
            claims = pd.read_sql_query("SELECT * FROM claims", conn)
            selected_claim = st.selectbox("Select claim to update", claims['Claim_ID'])
            
            claim_data = pd.read_sql_query(
                f"SELECT * FROM claims WHERE Claim_ID = {selected_claim}", conn
            ).iloc[0]
            
            with st.form("update_claim"):
                food_id = st.number_input("Food ID", min_value=1, value=int(claim_data['Food_ID']))
                receiver_id = st.number_input("Receiver ID", min_value=1, value=int(claim_data['Receiver_ID']))
                status = st.selectbox("Status", ["Pending", "Completed", "Cancelled"], 
                                    index=["Pending", "Completed", "Cancelled"].index(claim_data['Status']))
                timestamp = st.date_input("Timestamp", value=pd.to_datetime(claim_data['Timestamp']))
                
                submitted = st.form_submit_button("Update Claim")
                if submitted:
                    cursor = conn.cursor()
                    cursor.execute(
                        """UPDATE claims SET Food_ID = ?, Receiver_ID = ?, Status = ?, 
                        Timestamp = ? WHERE Claim_ID = ?""",
                        (food_id, receiver_id, status, timestamp, selected_claim)
                    )
                    conn.commit()
                    st.success("Claim updated successfully!")
        
        conn.close()
        
    elif selected_crud == "Delete Record":
        st.subheader("Delete Record")
        
        table_options = ["providers", "food", "receivers", "claims"]
        selected_table = st.selectbox("Select table to delete from", table_options)
        
        conn = get_db_connection()
        
        if selected_table == "providers":
            providers = pd.read_sql_query("SELECT * FROM providers", conn)
            selected_provider = st.selectbox("Select provider to delete", providers['Provider_ID'])
            
            if st.button("Delete Provider"):
                cursor = conn.cursor()
                # First check if provider has food items
                food_count = pd.read_sql_query(
                    f"SELECT COUNT(*) as count FROM food WHERE Provider_ID = {selected_provider}", conn
                )['count'][0]
                
                if food_count > 0:
                    st.warning(f"Cannot delete provider. There are {food_count} food items associated with this provider.")
                else:
                    cursor.execute(f"DELETE FROM providers WHERE Provider_ID = {selected_provider}")
                    conn.commit()
                    st.success("Provider deleted successfully!")
        
        elif selected_table == "food":
            food_items = pd.read_sql_query("SELECT * FROM food", conn)
            selected_food = st.selectbox("Select food item to delete", food_items['Food_ID'])
            
            if st.button("Delete Food Item"):
                cursor = conn.cursor()
                # First check if food item has claims
                claim_count = pd.read_sql_query(
                    f"SELECT COUNT(*) as count FROM claims WHERE Food_ID = {selected_food}", conn
                )['count'][0]
                
                if claim_count > 0:
                    st.warning(f"Cannot delete food item. There are {claim_count} claims associated with this food item.")
                else:
                    cursor.execute(f"DELETE FROM food WHERE Food_ID = {selected_food}")
                    conn.commit()
                    st.success("Food item deleted successfully!")
        
        elif selected_table == "receivers":
            receivers = pd.read_sql_query("SELECT * FROM receivers", conn)
            selected_receiver = st.selectbox("Select receiver to delete", receivers['Receiver_ID'])
            
            if st.button("Delete Receiver"):
                cursor = conn.cursor()
                # First check if receiver has claims
                claim_count = pd.read_sql_query(
                    f"SELECT COUNT(*) as count FROM claims WHERE Receiver_ID = {selected_receiver}", conn
                )['count'][0]
                
                if claim_count > 0:
                    st.warning(f"Cannot delete receiver. There are {claim_count} claims associated with this receiver.")
                else:
                    cursor.execute(f"DELETE FROM receivers WHERE Receiver_ID = {selected_receiver}")
                    conn.commit()
                    st.success("Receiver deleted successfully!")
        
        elif selected_table == "claims":
            claims = pd.read_sql_query("SELECT * FROM claims", conn)
            selected_claim = st.selectbox("Select claim to delete", claims['Claim_ID'])
            
            if st.button("Delete Claim"):
                cursor = conn.cursor()
                cursor.execute(f"DELETE FROM claims WHERE Claim_ID = {selected_claim}")
                conn.commit()
                st.success("Claim deleted successfully!")

# SQL Queries & Visualization
def show_queries_visualization():
    st.title("📈 SQL Queries & Visualization")
    
    query_options = {
        "Food Providers by City": """
            SELECT City, COUNT(*) as Count 
            FROM providers 
            GROUP BY City 
            ORDER BY Count DESC
        """,
        "Food Receivers by City": """
            SELECT COUNT(*) AS Receiver_count, City
            FROM receivers
            GROUP BY City
            ORDER BY Receiver_count DESC
        """,
        "Provider Types Distribution": """
            SELECT COUNT(*) AS Provider_Count, Type
            FROM providers
            GROUP BY Type
            ORDER BY Provider_Count DESC
        """,
        "Top Receivers by Claims": """
            SELECT r.Name, r.Type, COUNT(c.Claim_ID) as Claims 
            FROM receivers r 
            JOIN claims c ON r.Receiver_ID = c.Receiver_ID 
            WHERE c.Status = 'Completed' 
            GROUP BY r.Receiver_ID 
            ORDER BY Claims DESC 
            LIMIT 10
        """,
        "Total Food Available": """
            SELECT SUM(Quantity) Total_Available_Food
            FROM food
        """,
        "Cities with Most Food Listings": """
            SELECT COUNT(Food_Name) AS Number_Of_Listing, Location
            FROM food
            GROUP BY Location
            ORDER BY Number_Of_Listing DESC
        """,
        "Most Common Food Types": """
            SELECT DISTINCT Food_Type AS Food_Type,
                COUNT(*) AS Number_Of_Listings,
                SUM(QUANTITY) AS Total_Quantity
            FROM food
            GROUP BY Food_Type
            ORDER BY Number_Of_Listings DESC
        """,
        "Claims per Food Item": """
            SELECT f.Food_ID, f.Food_Name, f.Food_Type, COUNT(Food_Name) Claims
            FROM claims c
            JOIN food f ON c.Food_ID = f.Food_ID
            GROUP BY c.Food_ID
            ORDER BY Claims DESC
        """,
        "Top Providers by Successful Claims": """
            SELECT Count(c.Claim_ID) AS Successful_Claims, p.Name, p.Provider_ID, p.Type
            FROM food f
            JOIN providers p ON f.Provider_ID = p.Provider_ID
            JOIN claims c ON c.Food_ID = f.Food_ID
            WHERE c.Status = 'Completed'
            GROUP BY p.Provider_ID, p.Name, p.Type
            ORDER BY Successful_Claims DESC
            LIMIT 10
        """,
        "Claim Status Distribution": """
            SELECT COUNT(*) Claim_Count, 
                (COUNT(*) * 100 / (SELECT COUNT(*) FROM claims)) Percentage,
                Status
            FROM claims
            GROUP BY Status
        """,
        "Average Quantity Claimed per Receiver": """
            SELECT ROUND(AVG(Total_Quantity), 2) AS Avg_Quantity_Per_Receiver
            FROM (
                SELECT c.Receiver_ID, SUM(Quantity) AS Total_Quantity
                FROM claims c
                JOIN food f ON c.Food_ID = f.Food_ID
                WHERE c.Status = 'Completed'
                GROUP BY c.Receiver_ID
            )
        """,
        "Most Claimed Meal Types": """
            SELECT COUNT(*) AS Total_Claimed, f.Meal_Type
            FROM claims c
            JOIN food f ON c.Food_ID = f.Food_ID
            WHERE c.Status = 'Completed'
            GROUP BY f.Meal_Type
            ORDER BY Total_Claimed DESC
        """,
        "Food Donated by Provider": """
            SELECT p.Name, p.Type, SUM(Quantity) AS Total_Quantity
            FROM food f
            JOIN providers p ON f.Provider_ID = p.Provider_ID
            GROUP BY p.Provider_ID
            ORDER BY Total_Quantity DESC
        """
    }
    
    selected_query = st.selectbox("Select a predefined query", list(query_options.keys()))
    
    conn = get_db_connection()
    df = pd.read_sql_query(query_options[selected_query], conn)
    conn.close()
    
    st.subheader("Query Results")
    st.dataframe(df, use_container_width=True)
    
    st.subheader("Visualization")
    
    if selected_query == "Food Providers by City":
        fig = px.bar(df, x='City', y='Count', title='Food Providers by City')
        st.plotly_chart(fig, use_container_width=True)
        
    elif selected_query == "Food Receivers by City":
        fig = px.bar(df, x='City', y='Receiver_count', title='Food Receivers by City')
        st.plotly_chart(fig, use_container_width=True)
        
    elif selected_query == "Provider Types Distribution":
        fig = px.pie(df, values='Provider_Count', names='Type', title='Provider Types Distribution')
        st.plotly_chart(fig, use_container_width=True)
        
    elif selected_query == "Top Receivers by Claims":
        fig = px.bar(df, x='Name', y='Claims', title='Top Receivers by Number of Claims')
        st.plotly_chart(fig, use_container_width=True)
        
    elif selected_query == "Total Food Available":
        st.metric("Total Food Available", df['Total_Available_Food'][0])
        
    elif selected_query == "Cities with Most Food Listings":
        fig = px.bar(df, x='Location', y='Number_Of_Listing', 
                    title='Cities with Most Food Listings')
        st.plotly_chart(fig, use_container_width=True)
        
    elif selected_query == "Most Common Food Types":
        fig = px.bar(df, x='Food_Type', y='Number_Of_Listings', 
                    title='Most Common Food Types by Listings')
        st.plotly_chart(fig, use_container_width=True)
        
        # Additional visualization for quantity
        fig2 = px.bar(df, x='Food_Type', y='Total_Quantity', 
                     title='Total Quantity by Food Type')
        st.plotly_chart(fig2, use_container_width=True)
        
    elif selected_query == "Claims per Food Item":
        fig = px.bar(df.head(10), x='Food_Name', y='Claims', 
                    title='Top 10 Most Claimed Food Items')
        st.plotly_chart(fig, use_container_width=True)
        
    elif selected_query == "Top Providers by Successful Claims":
        fig = px.bar(df, x='Name', y='Successful_Claims', 
                    title='Top Providers by Successful Claims')
        st.plotly_chart(fig, use_container_width=True)
        
    elif selected_query == "Claim Status Distribution":
        fig = px.pie(df, values='Claim_Count', names='Status', 
                    title='Claim Status Distribution')
        st.plotly_chart(fig, use_container_width=True)
        
        # Show percentages as well
        st.write("Percentage Breakdown:")
        for _, row in df.iterrows():
            st.write(f"{row['Status']}: {row['Percentage']:.2f}%")
            
    elif selected_query == "Average Quantity Claimed per Receiver":
        st.metric("Average Quantity Claimed per Receiver", df['Avg_Quantity_Per_Receiver'][0])
        
    elif selected_query == "Most Claimed Meal Types":
        fig = px.pie(df, values='Total_Claimed', names='Meal_Type', 
                    title='Most Claimed Meal Types')
        st.plotly_chart(fig, use_container_width=True)
        
    elif selected_query == "Food Donated by Provider":
        fig = px.bar(df.head(10), x='Name', y='Total_Quantity', 
                    title='Top 10 Providers by Food Donated')
        st.plotly_chart(fig, use_container_width=True)

# Learner SQL Queries
def show_learner_queries():
    st.title("🎓 Learner SQL Queries")
    
    st.markdown("""
    Practice your SQL skills with these common queries for food wastage analysis:
    """)
    
    queries = {
        "City with most food listings": """
            SELECT p.City, COUNT(f.Food_ID) as Listings 
            FROM food f 
            JOIN providers p ON f.Provider_ID = p.Provider_ID 
            GROUP BY p.City 
            ORDER BY Listings DESC 
            LIMIT 1
        """,
        "Most commonly available food types": """
            SELECT Food_Type, COUNT(*) as Count 
            FROM food 
            GROUP BY Food_Type 
            ORDER BY Count DESC
        """,
        "Average quantity of food claimed per receiver": """
            SELECT ROUND(AVG(total_quantity), 2) as avg_quantity 
            FROM (
                SELECT c.Receiver_ID, SUM(f.Quantity) as total_quantity 
                FROM claims c 
                JOIN food f ON c.Food_ID = f.Food_ID 
                WHERE c.Status = 'Completed' 
                GROUP BY c.Receiver_ID
            )
        """,
        "Provider with the most successful claims": """
            SELECT p.Name, p.Type, COUNT(c.Claim_ID) as Claims 
            FROM providers p 
            JOIN food f ON p.Provider_ID = f.Provider_ID 
            JOIN claims c ON f.Food_ID = c.Food_ID 
            WHERE c.Status = 'Completed' 
            GROUP BY p.Provider_ID 
            ORDER BY Claims DESC 
            LIMIT 1
        """
    }
    
    for query_name, query in queries.items():
        with st.expander(query_name):
            st.code(query, language="sql")
            
            if st.button("Run", key=query_name):
                conn = get_db_connection()
                try:
                    df = pd.read_sql_query(query, conn)
                    st.dataframe(df, use_container_width=True)
                except Exception as e:
                    st.error(f"Error executing query: {e}")
                finally:
                    conn.close()


if __name__ == "__main__":
    main()
