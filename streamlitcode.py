import streamlit as st
import mysql.connector
import pandas as pd

# Function to connect to the database
def connect_to_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="csv_db 10"
        )
        st.success("Connected to database!")
        return conn
    except Exception as e:
        st.error(f"Failed to connect to database: {e}")
        return None

# Function to fetch data from the database
def fetch_data(query):
    conn = connect_to_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute(query)
        out = cursor.fetchall()
        df = pd.DataFrame(out, columns=[i[0] for i in cursor.description])
        cursor.close()
        conn.close()
        return df
    else:
        return None

# Streamlit App Layout
def main():
    # Apply CSS to control the layout and table width
    st.markdown(
        """
        <style>
        /* Set the width of the main content */
        .main .block-container {
            max-width: 90%;
            padding: 1rem 2rem;
        }
        /* Make the dataframe scrollable within the content */
        .dataframe-container {
            overflow-x: auto;
        }
        </style>
        """, unsafe_allow_html=True
    )

    st.title("Bus Routes Database Viewer")
    st.write("This app allows you to view and filter bus routes data from a SQL database.")

    # Query to fetch all data from the SQL table
    query = "SELECT * FROM bus_routes;"
    df = fetch_data(query)

    # If no data, handle gracefully
    if df is None or df.empty:
        st.error("No data found in the database.")
    else:
        # Normalize column names by converting them to lowercase
        df.columns = df.columns.str.strip().str.lower()

        # Create a sidebar for filtering options
        st.sidebar.header("Filter Options")

        # Step 1: Filter by state
        state = st.sidebar.selectbox("Filter by state", options=[None] + list(df['state'].dropna().unique()))
        filtered_df = df[df['state'] == state] if state else df

        # Initialize route_name to None
        route_name = None
        
        # Step 2: Filter by route_name based on selected state
        if state:
            route_names = filtered_df['route_name'].dropna().unique()
            route_name = st.sidebar.selectbox("Filter by route_name", options=[None] + list(route_names))
            if route_name:
                filtered_df = filtered_df[filtered_df['route_name'] == route_name]

        # Step 3: Optional Filter by busname
        if state or route_name:
            busnames = filtered_df['busname'].dropna().unique()
            busname = st.sidebar.selectbox("Filter by busname (optional)", options=[None] + list(busnames))
            if busname:
                filtered_df = filtered_df[filtered_df['busname'] == busname]

        # Step 4: Filter by bustype
        bustypes = filtered_df['bustype'].dropna().unique()
        bustype = st.sidebar.selectbox("Filter by bustype", options=[None] + list(bustypes))
        if bustype:
            filtered_df = filtered_df[filtered_df['bustype'] == bustype]

        # Step 5: Filter by departing_time
        departing_times = filtered_df['departing_time'].dropna().unique()
        departing_time = st.sidebar.selectbox("Filter by departing_time", options=[None] + list(departing_times))
        if departing_time:
            filtered_df = filtered_df[filtered_df['departing_time'] == departing_time]

        # Step 6: Filter by departure_location
        departure_locations = filtered_df['departure_location'].dropna().unique()
        departure_location = st.sidebar.selectbox("Filter by departure_location", options=[None] + list(departure_locations))
        if departure_location:
            filtered_df = filtered_df[filtered_df['departure_location'] == departure_location]

        # Step 7: Filter by reaching_time
        reaching_times = filtered_df['reaching_time'].dropna().unique()
        reaching_time = st.sidebar.selectbox("Filter by reaching_time", options=[None] + list(reaching_times))
        if reaching_time:
            filtered_df = filtered_df[filtered_df['reaching_time'] == reaching_time]

        # Step 8: Filter by arrival_location
        arrival_locations = filtered_df['arrival_location'].dropna().unique()
        arrival_location = st.sidebar.selectbox("Filter by arrival_location", options=[None] + list(arrival_locations))
        if arrival_location:
            filtered_df = filtered_df[filtered_df['arrival_location'] == arrival_location]

        # Step 9: Filter by star_rating (numeric field)
        if not filtered_df['star_rating'].isna().all():
            min_star = float(filtered_df['star_rating'].min())
            max_star = float(filtered_df['star_rating'].max())
            if min_star != max_star:  # Only show slider if min != max
                star_rating = st.sidebar.slider("Filter by star_rating", min_value=min_star, max_value=max_star, value=(min_star, max_star))
                filtered_df = filtered_df[(filtered_df['star_rating'] >= star_rating[0]) & (filtered_df['star_rating'] <= star_rating[1])]
            else:
                st.sidebar.write(f"All records have the same star rating: {min_star}")

        # Step 10: Filter by price (numeric field)
        if not filtered_df['price'].isna().all():
            min_price = float(filtered_df['price'].min())
            max_price = float(filtered_df['price'].max())
            if min_price != max_price:  # Only show slider if min != max
                price = st.sidebar.slider("Filter by price", min_value=min_price, max_value=max_price, value=(min_price, max_price))
                filtered_df = filtered_df[(filtered_df['price'] >= price[0]) & (filtered_df['price'] <= price[1])]
            else:
                st.sidebar.write(f"All records have the same price: {min_price}")

        # Step 11: Filter by seats_available (numeric field)
        if not filtered_df['seats_available'].isna().all():
            min_seats = int(filtered_df['seats_available'].min())
            max_seats = int(filtered_df['seats_available'].max())
            if min_seats != max_seats:  # Only show slider if min != max
                seats_available = st.sidebar.slider("Filter by seats_available", min_value=min_seats, max_value=max_seats, value=(min_seats, max_seats))
                filtered_df = filtered_df[(filtered_df['seats_available'] >= seats_available[0]) & (filtered_df['seats_available'] <= seats_available[1])]
            else:
                st.sidebar.write(f"All records have the same number of seats available: {min_seats}")

        # Display the filtered data in a scrollable and responsive container
        st.write("### Filtered Bus Routes:")
        st.write(
            "<div class='dataframe-container'>",
            unsafe_allow_html=True
        )
        st.dataframe(filtered_df, use_container_width=True)  # Ensures the dataframe fits the container
        st.write("</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    main()

