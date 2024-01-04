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

with app.app_context():
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
                        FOREIGN KEY (gender_id) REFERENCES GENDER_TABLE(gender_id),
                        FOREIGN KEY (party_id) REFERENCES PARTY_TABLE(party_id)
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
        cur.executemany("INSERT INTO CANDIDATE_TABLE (candidate_id, name, gender_id, sitting, votes, party_id) VALUES (?, ?, ?, ?, ?, ?)", candidate_data)
        cur.executemany("INSERT INTO PARTY_TABLE (party_id, name) VALUES (?, ?)", party_data)
        cur.executemany("INSERT INTO CONSTITUENCY_TABLE (constituency_id, name, county_id, type) VALUES (?, ?, ?, ?)", constituency_data)
        cur.executemany("INSERT INTO COUNTY_TABLE (county_id, name, region_id, country_id) VALUES (?, ?, ?, ?)", county_data)
        cur.executemany("INSERT INTO REGION_TABLE (region_id, name) VALUES (?, ?)", region_data)
        cur.executemany("INSERT INTO COUNTRY_TABLE (country_id, name) VALUES (?, ?)", country_data)
        
        conn.commit()
        

        
        
        # Fetching party names and total votes for each party
        cur.execute("""
        SELECT PARTY_TABLE.name, SUM(CANDIDATE_TABLE.votes) as total_votes
        FROM PARTY_TABLE
        LEFT JOIN CANDIDATE_TABLE ON PARTY_TABLE.party_id = CANDIDATE_TABLE.party_id
        GROUP BY PARTY_TABLE.party_id
        ORDER BY total_votes DESC
        """)
    
        party_votes = cur.fetchall()
        
        # Calculating the total number of votes
        total_votes_result = cur.execute("SELECT SUM(votes) FROM CANDIDATE_TABLE").fetchone()
        total_votes = total_votes_result[0] if total_votes_result else 0
    
        # Closing the cursor and connection
        cur.close()
        conn.close()
        
        return render_template('index.html', party_votes=party_votes, total_votes=total_votes)
    


if __name__ == '__main__': 
	app.run(debug=False) 
