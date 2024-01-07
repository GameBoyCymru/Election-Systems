from flask import Flask, render_template
import sqlite3 
from myLists import candidate_data
from myLists import country_data
from myLists import region_data
from myLists import county_data
from myLists import constituency_data
from myLists import party_data
from myLists import gender_data

app = Flask(__name__) 

@app.route('/')
def index():
    
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
      
        
# Creating the Tables for the database
        
    cur.execute("DROP TABLE IF EXISTS GENDER_TABLE")
    cur.execute("""CREATE TABLE IF NOT EXISTS GENDER_TABLE (
                            gender_id INTEGER NOT NULL PRIMARY KEY,
                            gender_type VARCHAR(25) NOT NULL
                        );""")
    
    
    #drops table project if exists
    cur.execute("DROP TABLE IF EXISTS PARTY_TABLE")
    #runs create table script
    cur.execute("""CREATE TABLE IF NOT EXISTS PARTY_TABLE (
                    party_id INTEGER NOT NULL PRIMARY KEY,
                    name VARCHAR(50) NOT NULL
                )""")
    
    
    #drops table project if exists
    cur.execute("DROP TABLE IF EXISTS CANDIDATE_TABLE")
    #runs create table script
    cur.execute("""CREATE TABLE IF NOT EXISTS CANDIDATE_TABLE (
                    candidate_id INTEGER NOT NULL PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    gender_id INTEGER NOT NULL,
                    sitting VARCHAR(8) NOT NULL,
                    votes INTEGER NOT NULL,
                    party_id INTEGER NOT NULL,
                    constituency_id INTEGER NOT NULL,
                    FOREIGN KEY (gender_id) REFERENCES GENDER_TABLE(gender_id),
                    FOREIGN KEY (party_id) REFERENCES PARTY_TABLE(party_id),
                    FOREIGN KEY (constituency_id) REFERENCES CONSTITUENCY_TABLE(constituency_id)
                )""")

    
    #drops table project if exists
    cur.execute("DROP TABLE IF EXISTS REGION_TABLE")
    #runs create table script
    cur.execute("""CREATE TABLE IF NOT EXISTS REGION_TABLE (
                    region_id INTEGER NOT NULL PRIMARY KEY,
                    name VARCHAR(50) NOT NULL
                )""")
    

    #drops table project if exists
    cur.execute("DROP TABLE IF EXISTS COUNTRY_TABLE")
    #runs create table script
    cur.execute("""CREATE TABLE IF NOT EXISTS COUNTRY_TABLE (
                    country_id INTEGER NOT NULL PRIMARY KEY,
                    name VARCHAR(50) NOT NULL
                )""")
    
    
    #drops table project if exists
    cur.execute("DROP TABLE IF EXISTS COUNTY_TABLE")
    #runs create table script
    cur.execute("""CREATE TABLE IF NOT EXISTS COUNTY_TABLE (
                    county_id INTEGER NOT NULL PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    region_id INTEGER NOT NULL,
                    country_id INTEGER NOT NULL,
                    FOREIGN KEY (region_id) REFERENCES REGION_TABLE(region_id),
                    FOREIGN KEY (country_id) REFERENCES REGION_TABLE(country_id)
                )""")
    
    
    #drops table project if exists
    cur.execute("DROP TABLE IF EXISTS CONSTITUENCY_TABLE")
    #runs create table script
    cur.execute("""CREATE TABLE IF NOT EXISTS CONSTITUENCY_TABLE (
                    constituency_id INTEGER NOT NULL PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    county_id INTEGER NOT NULL,
                    type VARCHAR(8) NOT NULL,
                    FOREIGN KEY (county_id) REFERENCES COUNTY_TABLE(county_id)
                )""")
   
    
    #drops table project if exists
    cur.execute("DROP TABLE IF EXISTS PARTYCONSTITUENCY_TABLE")
    #runs create table script
    cur.execute("""CREATE TABLE IF NOT EXISTS PARTYCONSTITUENCY_TABLE (
                party_id INTEGER NOT NULL,
                constituency_id INTEGER NOT NULL,
                PRIMARY KEY (party_id, constituency_id),
                FOREIGN KEY (party_id) REFERENCES PARTY_TABLE(party_id),
                FOREIGN KEY (constituency_id) REFERENCES CONSTITUENCY_TABLE(constituency_id)
                )""")
   
    
    cur.executemany("INSERT INTO GENDER_TABLE (gender_id, gender_type) VALUES (?, ?)", gender_data)
    cur.executemany("INSERT INTO CANDIDATE_TABLE (candidate_id, name, gender_id, sitting, votes, party_id, constituency_id) VALUES (?, ?, ?, ?, ?, ?, ?)", candidate_data)
    cur.executemany("INSERT INTO PARTY_TABLE (party_id, name) VALUES (?, ?)", party_data)
    cur.executemany("INSERT INTO CONSTITUENCY_TABLE (constituency_id, name, county_id, type) VALUES (?, ?, ?, ?)", constituency_data)
    cur.executemany("INSERT INTO COUNTY_TABLE (county_id, name, region_id, country_id) VALUES (?, ?, ?, ?)", county_data)
    cur.executemany("INSERT INTO REGION_TABLE (region_id, name) VALUES (?, ?)", region_data)
    cur.executemany("INSERT INTO COUNTRY_TABLE (country_id, name) VALUES (?, ?)", country_data)
    
    conn.commit()
    
    # Closing the cursor and connection
    cur.close()
    conn.close()
    
    menu_items = [
        "First past the post by Constituency",
        "Simple Proportional Representation (All Seats)",
        "Simple Proportional Representation (All Seats) with a threshold of 5%",
        "Proportional Representation (By County)",
        "Proportional Representation (By Region)",
        "Proportional Representation (By Country)",
        "Largest Remainder (By County)",
        "Largest Remainder (By Region)",
        "Largest Remainder (By Country)",
        "D’Hondt (By County)",
        "D’Hondt (By Region)",
        "D’Hondt (By Country)",
        "Webster (By Country)"
    ]

    return render_template('index.html', menu_items=menu_items)

# The route is the link to the webpage (html file)
# Always begin with @app.route and it ends with a "return render_template......"


# Route for the "First past the post by Constituency" page
@app.route('/first_past_the_post')
def first_past_the_post():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()

 # SQL query to fetch party name, total votes, and seats won for each constituency
        cur.execute("""
            SELECT
                c.party_id,
                p.name AS party_name,
                SUM(c.votes) AS total_votes,
                COUNT(DISTINCT c.constituency_id) AS seats_won
            FROM
                CANDIDATE_TABLE c
            JOIN
                PARTY_TABLE p ON c.party_id = p.party_id
            WHERE
                (c.constituency_id, c.votes) = (
                    SELECT
                        constituency_id,
                        MAX(votes)
                    FROM
                        CANDIDATE_TABLE
                    WHERE
                        constituency_id = c.constituency_id
                    GROUP BY
                        constituency_id
                )
            GROUP BY
                c.party_id
            ORDER BY
                seats_won DESC
        """)
        party_results = cur.fetchall()

    return render_template('first_past_the_post.html', party_results=party_results)

    

if __name__ == '__main__':
    app.run(debug=True)
