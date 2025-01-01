import pandas as pd
from sqlalchemy import create_engine


# Load the CSV file
csv_file_path = 'data/breach_data.csv'  # Replace with the correct path to your CSV file
data = pd.read_csv(csv_file_path)

# Database connection URL
db_url = "mysql+pymysql://root:ServBay.dev@127.0.0.1:3306/breach_db"  # Replace with your database URL
engine = create_engine(db_url)

# Define the table name
table_name = 'breach_data'

# Insert data into the database
data.to_sql(table_name, con=engine, if_exists='replace', index=False)

print("Data inserted successfully into the database.")
