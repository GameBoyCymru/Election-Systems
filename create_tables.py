import sqlite3
import csv

conn = sqlite3.connect('database.db')
cur = conn.cursor()

# drops table GENDER_TABLE if exists and creates it
cur.execute("DROP TABLE IF EXISTS GENDER_TABLE")
cur.execute("""CREATE TABLE IF NOT EXISTS GENDER_TABLE (
                    gender_id varchar(5) NOT NULL PRIMARY KEY,
                    gender_type text NOT NULL
                );""")

# drops table PARTY_TABLE if exists and creates it
cur.execute("DROP TABLE IF EXISTS PARTY_TABLE")
cur.execute("""CREATE TABLE IF NOT EXISTS PARTY_TABLE (
            party_id varchar(5) NOT NULL PRIMARY KEY,
            name text NOT NULL
        )""")

# drops table CANDIDATE_TABLE if exists and creates it
cur.execute("DROP TABLE IF EXISTS CANDIDATE_TABLE")
cur.execute("""CREATE TABLE IF NOT EXISTS CANDIDATE_TABLE (
            candidate_id varchar(5) NOT NULL PRIMARY KEY,
            name text NOT NULL,
            gender_id varchar(5) NOT NULL,
            sitting VARCHAR(3) NOT NULL,
            votes INTEGER NOT NULL,
            party_id varchar(5) NOT NULL,
            constituency_id varchar(5) NOT NULL,
            county_id varchar(5) NOT NULL,
            region_id varchar(5) NOT NULL,
            country_id varchar(5) NOT NULL,
            FOREIGN KEY (gender_id) REFERENCES GENDER_TABLE(gender_id),
            FOREIGN KEY (party_id) REFERENCES PARTY_TABLE(party_id),
            FOREIGN KEY (constituency_id) REFERENCES CONSTITUENCY_TABLE(constituency_id),
            FOREIGN KEY (county_id) REFERENCES COUNTY_TABLE(county_id),
            FOREIGN KEY (region_id) REFERENCES REGION_TABLE(region_id),
            FOREIGN KEY (country_id) REFERENCES COUNTRY_TABLE(country_id)
        )""")

# drops table REGION_TABLE if exists and creates it
cur.execute("DROP TABLE IF EXISTS REGION_TABLE")
cur.execute("""CREATE TABLE IF NOT EXISTS REGION_TABLE (
            region_id varchar(5) NOT NULL PRIMARY KEY,
            name text NOT NULL
        )""")

# drops table COUNTRY_TABLE if exists and creates it
cur.execute("DROP TABLE IF EXISTS COUNTRY_TABLE")
cur.execute("""CREATE TABLE IF NOT EXISTS COUNTRY_TABLE (
            country_id varchar(5) NOT NULL PRIMARY KEY,
            name text NOT NULL
        )""")

# drops table COUNTY_TABLE if exists and creates it
cur.execute("DROP TABLE IF EXISTS COUNTY_TABLE")
cur.execute("""CREATE TABLE IF NOT EXISTS COUNTY_TABLE (
            county_id varchar(5) NOT NULL PRIMARY KEY,
            name text NOT NULL
        )""")

# drops table CONSTITUENCY_TABLE if exists and creates it
cur.execute("DROP TABLE IF EXISTS CONSTITUENCY_TABLE")
cur.execute("""CREATE TABLE IF NOT EXISTS CONSTITUENCY_TABLE (
            constituency_id varchar(5) NOT NULL PRIMARY KEY,
            name text NOT NULL,
            type VARCHAR(15) NOT NULL
            )""")

# drops table RESULTS_TABLE if exists
cur.execute("DROP TABLE IF EXISTS RESULTS_TABLE")
cur.execute("""
            CREATE TABLE RESULTS_TABLE (
                election_system_name text NOT NULL,
                name text NOT NULL,
                votes INTEGER,
                seats INTEGER,
                vote_percentages REAL,
                seat_percentages REAL,
                vote_seat_differences REAL,
                seat_differences_from_winner INTEGER,
                is_different_from_winner VARCHAR(3),
                total_valid_votes INTEGER,
                party_with_most_seats text
            )
        """)

# inserts data from the gender_data csv into a list
with open('data/gender_data.csv', newline='') as csvfile:
    gender_data = [(int(row[0]), row[1]) for row in csv.reader(csvfile)]

# inserts data from the candidate_data csv into a list
with open('data/candidate_data.csv', newline='', encoding='utf-8-sig') as csvfile:
    candidate_data = [(int(row[0]), row[1], int(row[2]), row[3], int(row[4]), int(row[5]), int(row[6]), int(row[7]),
                       int(row[8]), int(row[9])) for row in csv.reader(csvfile)]

# inserts data from the party_data csv into a list
with open('data/party_data.csv', newline='', encoding='utf-8-sig') as csvfile:
    party_data = [(int(row[0]), row[1]) for row in csv.reader(csvfile)]

# inserts data from the constituency_data csv into a list
with open('data/constituency_data.csv', newline='', encoding='utf-8-sig') as csvfile:
    constituency_data = [(int(row[0]), row[1], row[2]) for row in csv.reader(csvfile)]

# inserts data from the region_data csv into a list
with open('data/region_data.csv', newline='', encoding='utf-8-sig') as csvfile:
    region_data = [(int(row[0]), row[1]) for row in csv.reader(csvfile)]

# inserts data from the county_data csv into a list
with open('data/county_data.csv', newline='', encoding='utf-8-sig') as csvfile:
    county_data = [(int(row[0]), row[1]) for row in csv.reader(csvfile)]

# inserts data from the country_data csv into a list
with open('data/country_data.csv', newline='', encoding='utf-8-sig') as csvfile:
    country_data = [(int(row[0]), row[1]) for row in csv.reader(csvfile)]



# inserts all the data from the lists into the relevant tables
cur.executemany("INSERT INTO GENDER_TABLE (gender_id, gender_type) VALUES (?,?);", gender_data)
cur.executemany("INSERT INTO CANDIDATE_TABLE (candidate_id, name, gender_id, sitting, votes, party_id, constituency_id, county_id, region_id, country_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", candidate_data)
cur.executemany("INSERT INTO PARTY_TABLE (party_id, name) VALUES (?, ?)", party_data)
cur.executemany("INSERT INTO CONSTITUENCY_TABLE (constituency_id, name, type) VALUES (?, ?, ?)", constituency_data)
cur.executemany("INSERT INTO COUNTY_TABLE (county_id, name) VALUES (?, ?)", county_data)
cur.executemany("INSERT INTO REGION_TABLE (region_id, name) VALUES (?, ?)", region_data)
cur.executemany("INSERT INTO COUNTRY_TABLE (country_id, name) VALUES (?, ?)", country_data)

conn.commit()
cur.close()
conn.close()
