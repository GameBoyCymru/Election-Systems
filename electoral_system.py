from flask import Flask, render_template
import sqlite3
import csv 
import math


app = Flask(__name__) 


conn = sqlite3.connect('database.db')
cur = conn.cursor()

# Creating the Tables for the database

# drops table GENDER_TABLE if exists
        
cur.execute("DROP TABLE IF EXISTS GENDER_TABLE")
cur.execute("""CREATE TABLE IF NOT EXISTS GENDER_TABLE (
                    gender_id INTEGER NOT NULL PRIMARY KEY,
                    gender_type VARCHAR(25) NOT NULL
                );""")


#drops table PARTY_TABLE if exists
cur.execute("DROP TABLE IF EXISTS PARTY_TABLE")
#runs create table script
cur.execute("""CREATE TABLE IF NOT EXISTS PARTY_TABLE (
            party_id INTEGER NOT NULL PRIMARY KEY,
            name VARCHAR(50) NOT NULL
        )""")


#drops table CANDIDATE_TABLE if exists
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
            county_id INTEGER NOT NULL,
            region_id INTEGER NOT NULL,
            country_id INTEGER NOT NULL,
            FOREIGN KEY (gender_id) REFERENCES GENDER_TABLE(gender_id),
            FOREIGN KEY (party_id) REFERENCES PARTY_TABLE(party_id),
            FOREIGN KEY (constituency_id) REFERENCES CONSTITUENCY_TABLE(constituency_id),
            FOREIGN KEY (county_id) REFERENCES COUNTY_TABLE(county_id),
            FOREIGN KEY (region_id) REFERENCES REGION_TABLE(region_id),
            FOREIGN KEY (country_id) REFERENCES COUNTRY_TABLE(country_id)
        )""")


#drops table REGION_TABLE if exists
cur.execute("DROP TABLE IF EXISTS REGION_TABLE")
#runs create table script
cur.execute("""CREATE TABLE IF NOT EXISTS REGION_TABLE (
            region_id INTEGER NOT NULL PRIMARY KEY,
            name VARCHAR(50) NOT NULL
        )""")


#drops table COUNTRY_TABLE if exists
cur.execute("DROP TABLE IF EXISTS COUNTRY_TABLE")
#runs create table script
cur.execute("""CREATE TABLE IF NOT EXISTS COUNTRY_TABLE (
            country_id INTEGER NOT NULL PRIMARY KEY,
            name VARCHAR(50) NOT NULL
        )""")


#drops table COUNTY_TABLE if exists
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


#drops table CONSTITUENCY_TABLE if exists
cur.execute("DROP TABLE IF EXISTS CONSTITUENCY_TABLE")
#runs create table script
cur.execute("""CREATE TABLE IF NOT EXISTS CONSTITUENCY_TABLE (
            constituency_id INTEGER NOT NULL PRIMARY KEY,
            name VARCHAR(50) NOT NULL,
            county_id INTEGER NOT NULL,
            type VARCHAR(8) NOT NULL,
            FOREIGN KEY (county_id) REFERENCES COUNTY_TABLE(county_id)
        )""")
   

#drops table PARTYCONSTITUENCY_TABLE if exists
cur.execute("DROP TABLE IF EXISTS PARTYCONSTITUENCY_TABLE")
#runs create table script
cur.execute("""CREATE TABLE IF NOT EXISTS PARTYCONSTITUENCY_TABLE (
        party_id INTEGER NOT NULL,
        constituency_id INTEGER NOT NULL,
        PRIMARY KEY (party_id, constituency_id),
        FOREIGN KEY (party_id) REFERENCES PARTY_TABLE(party_id),
        FOREIGN KEY (constituency_id) REFERENCES CONSTITUENCY_TABLE(constituency_id)
        )""")
   


#drops table RESULTS_TABLE if exists
cur.execute("DROP TABLE IF EXISTS RESULTS_TABLE")
#runs create table script
cur.execute("""
            CREATE TABLE RESULTS_TABLE (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                election_system_name TEXT NOT NULL,
                name TEXT NOT NULL,
                votes INTEGER,
                seats INTEGER,
                vote_percentages REAL,
                seat_percentages REAL,
                vote_seat_differences REAL,
                seat_differences_from_winner INTEGER,
                is_different_from_winner TEXT,
                total_valid_votes INTEGER,
                party_with_most_seats TEXT
            )
        """)

with open('data/gender_data.csv', newline='') as csvfile:
    gender_data = [(int(row[0]), row[1]) for row in csv.reader(csvfile)]

with open('data/candidate_data.csv', newline='', encoding='utf-8-sig') as csvfile:
    candidate_data = [(int(row[0]), row[1], int(row[2]), row[3], int(row[4]),  int(row[5]),  int(row[6]), int(row[7]),  int(row[8]),  int(row[9])) for row in csv.reader(csvfile)]

with open('data/party_data.csv', newline='', encoding='utf-8-sig') as csvfile:
    party_data = [(int(row[0]), row[1]) for row in csv.reader(csvfile)]
    
with open('data/constituency_data.csv', newline='' , encoding='utf-8-sig') as csvfile:
    constituency_data = [(int(row[0]), row[1], int(row[2]), row[3]) for row in csv.reader(csvfile)]
    
with open('data/region_data.csv', newline='', encoding='utf-8-sig') as csvfile:
    region_data = [(int(row[0]), row[1]) for row in csv.reader(csvfile)]
    

with open('data/county_data.csv', newline='', encoding='utf-8-sig') as csvfile:
    county_data = [(int(row[0]), row[1], int(row[2]), int(row[3])) for row in csv.reader(csvfile)]
    
with open('data/country_data.csv', newline='', encoding='utf-8-sig') as csvfile:
    country_data = [(int(row[0]), row[1]) for row in csv.reader(csvfile)]
    


cur.executemany("INSERT INTO GENDER_TABLE (gender_id, gender_type) VALUES (?,?);", gender_data)
cur.executemany("INSERT INTO CANDIDATE_TABLE (candidate_id, name, gender_id, sitting, votes, party_id, constituency_id, county_id, region_id, country_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", candidate_data)
cur.executemany("INSERT INTO PARTY_TABLE (party_id, name) VALUES (?, ?)", party_data)
cur.executemany("INSERT INTO CONSTITUENCY_TABLE (constituency_id, name, county_id, type) VALUES (?, ?, ?, ?)", constituency_data)
cur.executemany("INSERT INTO COUNTY_TABLE (county_id, name, region_id, country_id) VALUES (?, ?, ?, ?)", county_data)
cur.executemany("INSERT INTO REGION_TABLE (region_id, name) VALUES (?, ?)", region_data)
cur.executemany("INSERT INTO COUNTRY_TABLE (country_id, name) VALUES (?, ?)", country_data)




conn.commit()
cur.close()
conn.close()


def insert_into_results_table(election_system_name, name, votes, seats, vote_percentages, seat_percentages,vote_seat_differences, seat_differences_from_winner, is_different_from_winner, total_valid_votes, party_with_most_seats):
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO RESULTS_TABLE (election_system_name, name, votes, seats, vote_percentages, seat_percentages, vote_seat_differences, seat_differences_from_winner, is_different_from_winner, total_valid_votes, party_with_most_seats)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (election_system_name, name, votes, seats, vote_percentages, seat_percentages, vote_seat_differences, seat_differences_from_winner, is_different_from_winner, total_valid_votes, party_with_most_seats))


def first_past_the_post():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()

        disqualified_votes = 0  # To store the votes of disqualified votes


       # Calculate and display the total amount of votes
        cur.execute("SELECT SUM(votes) FROM CANDIDATE_TABLE")
        total_votes = cur.fetchone()[0]
        
        # Calculate the total number of seats
        cur.execute("SELECT COUNT(DISTINCT constituency_id) FROM CANDIDATE_TABLE")
        total_seats = cur.fetchone()[0]
        
        # Fetch the party results
        cur.execute("""
            SELECT
                p.name AS party_name,
                SUM(c.votes) AS total_votes
            FROM
                CANDIDATE_TABLE c
            JOIN
                PARTY_TABLE p ON c.party_id = p.party_id
            GROUP BY
                c.party_id
        """)
        party_results = cur.fetchall()
        
        # Calculate the percentage of votes for each party
        vote_percentages = {}
        for party_name, total_votes_party in party_results:
            if total_votes_party:
                vote_percentage = (total_votes_party / total_votes) * 100
                vote_percentages[party_name] = round(vote_percentage, 2)
            else:
                vote_percentages[party_name] = 0

        
        # Calculate the number of seats each party has won
        cur.execute("""
            SELECT
                p.name AS party_name,
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
        """)
        seats_results = dict(cur.fetchall())
        
        # Add parties without seats to the seats_results with default value 0
        for party_name, _ in party_results:
            seats_results.setdefault(party_name, 0)
            
        # Sort the seats_results dictionary by seats in descending order
        sorted_seats = sorted(seats_results.items(), key=lambda x: x[1], reverse=True)
        
        # Extract the party with the most seats
        party_with_most_seats, most_seats = sorted_seats[0] if sorted_seats else ("N/A", 0)
            
        # Calculate the difference between the percentage of votes and the percentage of seats for each party
        vote_seat_differences = {}
        for party_name in vote_percentages.keys():
            vote_percentage = vote_percentages[party_name]
            seat_percentage = (seats_results.get(party_name, 0) / total_seats) * 100
            difference = round(vote_percentage - seat_percentage, 2)
            vote_seat_differences[party_name] = difference
        
        # Calculate the difference in seats from the winner's seats for each party
        winner_seats = most_seats  # Assuming 'most_seats' is the number of seats the winner has
        seat_differences_from_winner = {}
        for party_name in seats_results.keys():
            party_seats = seats_results.get(party_name, 0)
            difference = party_seats - winner_seats
            seat_differences_from_winner[party_name] = difference
        
        is_different_from_winner = 'No' if party_with_most_seats == 'Conservative' else 'Yes'
        election_system_name = "First Past the Post"
        total_valid_votes = total_votes - disqualified_votes
        party_with_most_seats = max(seats_results, key=seats_results.get)


         # Insert the results into the database
        for party_name in sorted(vote_percentages.keys()):
            votes = dict(party_results).get(party_name, 0)
            seats = seats_results.get(party_name, 0)
            vote_percentage = vote_percentages[party_name]
            seat_percentage = (seats_results.get(party_name, 0) / total_seats) * 100
            vote_seat_difference = vote_seat_differences[party_name]
            seat_difference_from_winner = seat_differences_from_winner[party_name]
        
            insert_into_results_table(election_system_name, party_name, votes, seats, vote_percentage, seat_percentage, vote_seat_difference, seat_difference_from_winner, is_different_from_winner, total_valid_votes, party_with_most_seats)
        
        conn.commit()
   
        
def simple_proportional_representation():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()

        disqualified_votes = 0  # To store the votes of disqualified votes

        # Calculate and display the total amount of votes
        cur.execute("SELECT SUM(votes) FROM CANDIDATE_TABLE")
        total_votes = cur.fetchone()[0]

        # Calculate the total number of seats
        cur.execute("SELECT COUNT(DISTINCT constituency_id) FROM CANDIDATE_TABLE")
        total_seats = cur.fetchone()[0]

        # Fetch the party results
        cur.execute("""
            SELECT
                p.name AS party_name,
                SUM(c.votes) AS total_votes
            FROM
                CANDIDATE_TABLE c
            JOIN
                PARTY_TABLE p ON c.party_id = p.party_id
            GROUP BY
                c.party_id
        """)
        party_results = cur.fetchall()

        # Calculate the percentage of votes for each party
        vote_percentages = {}
        for party_name, total_votes_party in party_results:
            if total_votes_party:
                vote_percentage = (total_votes_party / total_votes) * 100
                vote_percentages[party_name] = round(vote_percentage, 2)
            else:
                vote_percentages[party_name] = 0

         # Calculate the number of seats each party has won based on the percentage of votes
        seats_results = {}
        for party_name, total_votes_party in party_results:
            if total_votes_party > 0:
                seat_count = int((total_votes_party / total_votes) * total_seats)
                seats_results[party_name] = seat_count
            else:
                seats_results[party_name] = 0

        # Add parties without seats to the seats_results with default value 0
        for party_name, _ in party_results:
            seats_results.setdefault(party_name, 0)


    
        # Sort the seats_results dictionary by seats in descending order
        sorted_seats = sorted(seats_results.items(), key=lambda x: x[1], reverse=True)
    
        # Extract the party with the most seats
        party_with_most_seats, most_seats = sorted_seats[0] if sorted_seats else ("N/A", 0)
    
        # Calculate the difference between the percentage of votes and the percentage of seats for each party
        vote_seat_differences = {}
        for party_name in vote_percentages.keys():
            vote_percentage = vote_percentages[party_name]
            seat_percentage = (seats_results.get(party_name, 0) / total_seats) * 100
            difference = round(vote_percentage - seat_percentage, 2)
            vote_seat_differences[party_name] = difference
    
        # Calculate the difference in seats from the winner's seats for each party
        winner_seats = most_seats  # Assuming 'most_seats' is the number of seats the winner has
        seat_differences_from_winner = {}
        for party_name in seats_results.keys():
            party_seats = seats_results.get(party_name, 0)
            difference = party_seats - winner_seats
            seat_differences_from_winner[party_name] = difference
            
        is_different_from_winner = 'No' if party_with_most_seats == 'Conservative' else 'Yes'
        election_system_name = "Simple Proportional Representation"
        total_valid_votes=total_votes - disqualified_votes
        party_with_most_seats = max(seats_results, key=seats_results.get)


         # Insert the results into the database
        for party_name in sorted(vote_percentages.keys()):
            votes = dict(party_results).get(party_name, 0)
            seats = seats_results.get(party_name, 0)
            vote_percentage = vote_percentages[party_name]
            seat_percentage = (seats_results.get(party_name, 0) / total_seats) * 100
            vote_seat_difference = vote_seat_differences[party_name]
            seat_difference_from_winner = seat_differences_from_winner[party_name]
        
            insert_into_results_table(election_system_name, party_name, votes, seats, vote_percentage, seat_percentage, vote_seat_difference, seat_difference_from_winner, is_different_from_winner, total_valid_votes, party_with_most_seats)
            
        conn.commit()
        
        
def proportional_representation_with_threshold():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()

        disqualified_votes = 0  # To store the votes of disqualified votes
        # Calculate and display the total amount of votes
        cur.execute("SELECT SUM(votes) FROM CANDIDATE_TABLE")
        total_votes = cur.fetchone()[0]

        # Calculate the total number of seats
        cur.execute("SELECT COUNT(DISTINCT constituency_id) FROM CANDIDATE_TABLE")
        total_seats = cur.fetchone()[0]

        # Fetch the party results
        cur.execute("""
            SELECT
                p.name AS party_name,
                SUM(c.votes) AS total_votes
            FROM
                CANDIDATE_TABLE c
            JOIN
                PARTY_TABLE p ON c.party_id = p.party_id
            GROUP BY
                c.party_id
        """)
        party_results = cur.fetchall()             
                
        

        # Calculate the number of seats each party has won based on the percentage of votes
        seats_results = {}
        vote_percentages = {}  # Initialize vote_percentages as an empty dictionary
        disqualified_votes = 0  # To store the votes of disqualified parties
        disqualified_parties = []  # To store the names of disqualified parties
        
        # First, disqualify parties with less than 5% of the total votes
        for party_name, total_votes_party in party_results[:]:  # Use a slice to iterate over a copy of party_results
            vote_percentage = (total_votes_party / total_votes) * 100

            # If the party has less than 5% of the total votes, disqualify them
            if vote_percentage < 5:
                disqualified_votes += total_votes_party
                disqualified_parties.append(party_name)
                seats_results[party_name] = 0  # Add disqualified party to seats_results with 0 seats
                vote_percentages[party_name] = 0.00  # Add disqualified party to vote_percentages with 0% votes
                party_results.remove((party_name, total_votes_party))  # Remove disqualified party from party_results
        
        # Then, calculate the seat count for the remaining parties
        for party_name, total_votes_party in party_results:
            if party_name not in disqualified_parties:
                # Use math.floor to round down to the nearest whole number
                seat_count = math.floor((total_votes_party / (total_votes - disqualified_votes)) * total_seats)
                seats_results[party_name] = seat_count


        # Add parties without seats to the seats_results with default value 0
        for party_name, _ in party_results:
            seats_results.setdefault(party_name, 0)
            
        # Calculate the percentage of votes for each party
        vote_percentages = {}
  
        for party_name, total_votes_party in party_results:
            if party_name not in disqualified_parties:
                if total_votes_party:
                    vote_percentage = (total_votes_party / (total_votes - disqualified_votes)) * 100
                    vote_percentages[party_name] = round(vote_percentage, 2)
                else:
                    vote_percentages[party_name] = 0.00

        # Sort the seats_results dictionary by seats in descending order
        sorted_seats = sorted(seats_results.items(), key=lambda x: x[1], reverse=True)
    
        # Extract the party with the most seats
        party_with_most_seats, most_seats = sorted_seats[0] if sorted_seats else ("N/A", 0)
    
        # Calculate the difference between the percentage of votes and the percentage of seats for each party
        vote_seat_differences = {}
        for party_name in vote_percentages.keys():
            vote_percentage = vote_percentages[party_name]
            seat_percentage = (seats_results.get(party_name, 0) / total_seats) * 100
            difference = round(vote_percentage - seat_percentage, 2)
            vote_seat_differences[party_name] = difference
    
        # Calculate the difference in seats from the winner's seats for each party
        winner_seats = most_seats  # Assuming 'most_seats' is the number of seats the winner has
        seat_differences_from_winner = {}
        for party_name in seats_results.keys():
            party_seats = seats_results.get(party_name, 0)
            difference = party_seats - winner_seats
            seat_differences_from_winner[party_name] = difference
    
        is_different_from_winner = 'No' if party_with_most_seats == 'Conservative' else 'Yes'
        election_system_name = "Simple Proportional Representation with 5% Threshold"
        total_valid_votes=total_votes - disqualified_votes
        party_with_most_seats = max(seats_results, key=seats_results.get)

        # Insert the results into the database
        for party_name in sorted(seats_results.keys()):  # Iterate over all parties, including disqualified ones
            votes = dict(party_results).get(party_name, 0)
            seats = seats_results.get(party_name, 0)
            vote_percentage = vote_percentages.get(party_name, 0)  # Use get method to avoid KeyError
            seat_percentage = (seats_results.get(party_name, 0) / total_seats) * 100
            vote_seat_difference = vote_seat_differences.get(party_name, 0)  # Use get method to avoid KeyError
            seat_difference_from_winner = seat_differences_from_winner.get(party_name, 0)  # Use get method to avoid KeyError

            insert_into_results_table(election_system_name, party_name, votes, seats, vote_percentage, seat_percentage, vote_seat_difference, seat_difference_from_winner, is_different_from_winner, total_valid_votes, party_with_most_seats)

        conn.commit()


def proportional_representation_by_county():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()

        # Get the total number of seats
        cur.execute("SELECT COUNT(DISTINCT constituency_id) FROM CANDIDATE_TABLE")
        total_seats = cur.fetchone()[0]

        # Fetch party results grouped by county
        cur.execute("""
            SELECT
                p.name AS party_name,
                c.county_id,
                SUM(c.votes) AS total_party_votes,
                COUNT(DISTINCT c.constituency_id) AS county_total_seats
            FROM
                CANDIDATE_TABLE c
            JOIN
                PARTY_TABLE p ON c.party_id = p.party_id
            JOIN
                CONSTITUENCY_TABLE con ON c.constituency_id = con.constituency_id
            GROUP BY
                c.party_id, c.county_id
        """)

        party_results_by_county = cur.fetchall()

        # Initialize a dictionary to store the total seats for each party
        party_total_seats = {}

        # Iterate over the results for each party and county
        for party_name, county_id, total_party_votes, county_total_seats in party_results_by_county:
            # Calculate the proportion of votes for the party in the county
            proportion_in_county = total_party_votes / sum([row[2] for row in party_results_by_county if row[1] == county_id])

            # Calculate the seats for the party in the county (rounded down)
            seats_in_county = math.floor(round(proportion_in_county * county_total_seats))

            # Update the total seats for the party
            party_total_seats[party_name] = party_total_seats.get(party_name, 0) + seats_in_county

        # Calculate total votes and total seats for the entire election
        total_votes = sum([row[2] for row in party_results_by_county])
        total_seats = sum(party_total_seats.values())

        # Insert the results into the database
        election_system_name = "Proportional Representation by County"
        total_valid_votes = total_votes
        party_with_most_seats = max(party_total_seats, key=party_total_seats.get)
        is_different_from_winner = 'No' if party_with_most_seats == 'Conservative' else 'Yes'

        for party_name, seats in party_total_seats.items():
            votes = sum([row[2] for row in party_results_by_county if row[0] == party_name])
            vote_percentage = (votes / total_votes) * 100
            seat_percentage = (seats / total_seats) * 100
            vote_seat_difference = round(vote_percentage - seat_percentage, 2)
            seat_difference_from_winner = seats - max(party_total_seats.values())

            # Insert into the RESULTS_TABLE
            cur.execute("""
                INSERT INTO RESULTS_TABLE
                (election_system_name, name, votes, seats, vote_percentages, seat_percentages, vote_seat_differences,
                 seat_differences_from_winner, is_different_from_winner, total_valid_votes, party_with_most_seats)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (election_system_name, party_name, votes, seats, vote_percentage, seat_percentage,
                  vote_seat_difference, seat_difference_from_winner, is_different_from_winner, total_valid_votes,
                  party_with_most_seats))

        conn.commit()

        
first_past_the_post()
simple_proportional_representation()
proportional_representation_with_threshold()
proportional_representation_by_county()

# Route for the "index" page
@app.route('/')
def index():
    
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


def get_results_from_table(election_system_name):
    with sqlite3.connect('database.db') as conn:
        
        
        cur = conn.cursor()
        cur.execute("SELECT * FROM RESULTS_TABLE WHERE election_system_name = ?", (election_system_name,))
        rows = cur.fetchall()

        
        cur.execute("SELECT SUM(votes) FROM CANDIDATE_TABLE")
        total_votes = cur.fetchone()[0]
        
        
        # Calculate the total number of seats from the seats awarded
        total_seats = sum(row[4] for row in rows)

        # Find the seat count of the party with the most seats
        most_seats = max(row[4] for row in rows)




    return rows, total_votes, total_seats, most_seats


@app.route('/results/<election_system_name>')
def results(election_system_name):
    # Replace underscores with spaces
    election_system_name = election_system_name.replace('_', ' ')
    results, total_votes, total_seats, most_seats = get_results_from_table(election_system_name)
    return render_template('results.html', election_system_name=election_system_name, results=results, total_votes=total_votes, total_seats=total_seats, most_seats=most_seats)







if __name__ == '__main__':
    app.run(debug=True)
