import requests
from bs4 import BeautifulSoup
import mysql.connector
import pandas as pd
#connecting to the database
connection = mysql.connector.connect(
    user=input("Enter the name of the user here: "),
    host=input("Enter host name: "),
    password=input("Enter your password here: "),
    database="jumiadec_2024"
)
conn = connection.cursor()
column_names = ["Name", "Discount_price", "Old_price", "Rating_stars"]#column_name for csv file
products = [] #empty list
filepath = r"C:\Users\HP\OneDrive\Desktop\jumia_dec_2024\jumia_laptors.csv"#file path for my csv file
# Function to create table if not exists
def createtables():
    conn.execute('''
    CREATE TABLE IF NOT EXISTS laptors(
        name VARCHAR(255),
        discount_price VARCHAR(255),
        actual_price VARCHAR(255),
        rating_stars VARCHAR(255)
    )
''')
createtables()
# Function to fetch data from a url that changes
def fetch_data(category, page_number):
    base_url = "https://www.jumia.com.ng/"
    full_url = f"{base_url}{category}/?page={page_number}#catalog-listing"
    response = requests.get(full_url)
    soup= BeautifulSoup(response.content, 'html.parser')
    data = soup.find_all("div", class_="info")
    for info in data:
        name = info.find("h3", class_="name").text
        discount_price = info.find("div", class_="prc").text
        old_price = info.find("div", class_="s-prc-w")
        actual_price = info.find("div", class_="old").text if old_price else "No old_price"
        rating = info.find("div", class_="rev")
        rating_stars = rating.find("div", class_="stars _s").text.split()[0] if rating else "No rating"
        query = '''
        INSERT INTO laptors(name, discount_price, actual_price, rating_stars)
        VALUES (%s, %s, %s, %s)
        '''
        dat_a = (name, discount_price, actual_price, rating_stars)
        conn.execute(query, dat_a)
        connection.commit()
        products.append({"Name":name,"Discount_price":discount_price,"Old-price":old_price,"Rating_stars":rating_stars})
# Function to loop through pages and fetch data
def url_loop(category, start_page=1, max_pages=50):
    for page_number in range(start_page, max_pages + 1):
        print(f"Fetching data from {category}, page {page_number}")
        fetch_data(category, page_number)
    df = pd.DataFrame(products, columns=column_names)
    df.to_csv(filepath, index=False)
    print(f"Data saved to {filepath}")
#main function
def main():
    category = input("Enter the category to replace 'phones-tablets' in the URL: ")
    start_page = int(input("Enter the start page number: "))
    max_pages = int(input("Enter the maximum number of pages to fetch: "))
    url_loop(category, start_page, max_pages)
if __name__ == "__main__":
    main() #main script logic