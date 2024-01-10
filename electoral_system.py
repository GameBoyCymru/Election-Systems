from flask import Flask, render_template
import sqlite3
import csv 
import math

app = Flask(__name__) 


conn = sqlite3.connect('database.db')
cur = conn.cursor()

candidate_data = open('candidate_data.csv')
candidate_data = csv.reader(candidate_data)

constituency_data = open('constituency_data.csv')
constituency_data = csv.reader(constituency_data)

county_data = open('county_data.csv')
county_data = csv.reader(county_data)

country_data = open('country_data.csv')
country_data = csv.reader(country_data)

party_data = open('party_data.csv')
party_data = csv.reader(party_data)

region_data = open('region_data.csv')
region_data = csv.reader(region_data)

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
   

gender_data = open('gender_data.csv')
with open('gender_data.csv', newline='') as csvfile:
    gender_data = [(int(row[0]), row[1]) for row in csv.reader(csvfile)]

candidate_data = open('candidate_data.csv')
with open('candidate_data.csv', newline='', encoding='utf-8-sig') as csvfile:
    candidate_data = [(int(row[0]), row[1], int(row[2]), row[3], int(row[4]),  int(row[5]),  int(row[6]),) for row in csv.reader(csvfile)]

    
party_data = open('party_data.csv')
with open('party_data.csv', newline='', encoding='utf-8-sig') as csvfile:
    party_data = [(int(row[0]), row[1]) for row in csv.reader(csvfile)]
    
constituency_data = open('constituency_data.csv')
with open('constituency_data.csv', newline='' , encoding='utf-8-sig') as csvfile:
    constituency_data = [(int(row[0]), row[1], int(row[2]), row[3]) for row in csv.reader(csvfile)]
    
region_data = open('region_data.csv')
with open('region_data.csv', newline='', encoding='utf-8-sig') as csvfile:
    region_data = [(int(row[0]), row[1]) for row in csv.reader(csvfile)]
    
county_data = open('county_data.csv')
with open('county_data.csv', newline='', encoding='utf-8-sig') as csvfile:
    county_data = [(int(row[0]), row[1], int(row[2]), int(row[3])) for row in csv.reader(csvfile)]
    
country_data = open('country_data.csv')
with open('country_data.csv', newline='', encoding='utf-8-sig') as csvfile:
    country_data = [(int(row[0]), row[1]) for row in csv.reader(csvfile)]
    

# Insert data into the tables regarding the data from the csv files
cur.executemany("INSERT INTO GENDER_TABLE (gender_id, gender_type) VALUES (?,?);", gender_data)
cur.executemany("INSERT INTO CANDIDATE_TABLE (candidate_id, name, gender_id, sitting, votes, party_id, constituency_id) VALUES (?, ?, ?, ?, ?, ?, ?)", candidate_data)
cur.executemany("INSERT INTO PARTY_TABLE (party_id, name) VALUES (?, ?)", party_data)
cur.executemany("INSERT INTO CONSTITUENCY_TABLE (constituency_id, name, county_id, type) VALUES (?, ?, ?, ?)", constituency_data)
cur.executemany("INSERT INTO COUNTY_TABLE (county_id, name, region_id, country_id) VALUES (?, ?, ?, ?)", county_data)
cur.executemany("INSERT INTO REGION_TABLE (region_id, name) VALUES (?, ?)", region_data)
cur.executemany("INSERT INTO COUNTRY_TABLE (country_id, name) VALUES (?, ?)", country_data)


# Create the table for the results of each election system
cur.execute("""
            CREATE TABLE IF NOT EXISTS RESULTS_TABLE (
                system_name TEXT,
                party_name TEXT,
                seats_won INTEGER,
                percentage_of_seats REAL,
                percentage_of_votes REAL,
                difference REAL
            )
        """)
       


conn.commit()
cur.close()
conn.close()




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


# Route for the "First past the post by Constituency" page
@app.route('/first_past_the_post')
def first_past_the_post():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()

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
        
        # Insert the results into the database
        for party_name in seats_results.keys():
            seats_won = seats_results[party_name]
            percentage_of_seats = (seats_won / total_seats) * 100
            percentage_of_votes = vote_percentages[party_name]
            difference = vote_seat_differences[party_name]
            cur.execute("""
                INSERT INTO RESULTS_TABLE (system_name, party_name, seats_won, percentage_of_seats, percentage_of_votes, difference)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('proportional_representation_with_threshold', party_name, seats_won, percentage_of_seats, percentage_of_votes, difference))
        conn.commit()
        
        return render_template('first_past_the_post.html', 
                               party_results=party_results, 
                               seats_results=seats_results, 
                               vote_percentages=vote_percentages, 
                               total_votes=total_votes, 
                               total_seats=total_seats, 
                               party_with_most_seats=party_with_most_seats, 
                               most_seats=most_seats, 
                               vote_seat_differences=vote_seat_differences, 
                               seat_differences_from_winner=seat_differences_from_winner)
























# Route for the "simple_proportional_representation" page
@app.route('/simple_proportional_representation')
def simple_proportional_representation():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()

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
            
        # Insert the results into the database
        for party_name in seats_results.keys():
            seats_won = seats_results[party_name]
            percentage_of_seats = (seats_won / total_seats) * 100
            percentage_of_votes = vote_percentages[party_name]
            difference = vote_seat_differences[party_name]
            cur.execute("""
                INSERT INTO RESULTS_TABLE (system_name, party_name, seats_won, percentage_of_seats, percentage_of_votes, difference)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('proportional_representation_with_threshold', party_name, seats_won, percentage_of_seats, percentage_of_votes, difference))
        conn.commit()
    
        return render_template('simple_proportional_representation.html',
                               party_results=party_results,
                               seats_results=seats_results,
                               vote_percentages=vote_percentages,
                               total_votes=total_votes,
                               total_seats=total_seats,
                               party_with_most_seats=party_with_most_seats,
                               most_seats=most_seats,
                               vote_seat_differences=vote_seat_differences,
                               seat_differences_from_winner=seat_differences_from_winner)





























# Route for the "simple_proportional_representation_with_threshold" page
@app.route('/proportional_representation_with_threshold')
def proportional_representation_with_threshold():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()

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
        disqualified_votes = 0  # To store the votes of disqualified parties
        disqualified_parties = []  # To store the names of disqualified parties
        
        # First, disqualify parties with less than 5% of the total votes
        for party_name, total_votes_party in party_results:
            vote_percentage = (total_votes_party / total_votes) * 100
        
            # If the party has less than 5% of the total votes, disqualify them
            if vote_percentage < 5:
                disqualified_votes += total_votes_party
                disqualified_parties.append(party_name)
        
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
            
        for party_name in seats_results.keys():
            seats_won = seats_results[party_name]
            percentage_of_seats = (seats_won / total_seats) * 100
            percentage_of_votes = vote_percentages[party_name] if party_name not in disqualified_parties else 0 
            difference = vote_seat_differences[party_name] if party_name not in disqualified_parties else 0
            cur.execute("""
                INSERT INTO RESULTS_TABLE (system_name, party_name, seats_won, percentage_of_seats, percentage_of_votes, difference)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ('proportional_representation_with_threshold', party_name, seats_won, percentage_of_seats, percentage_of_votes, difference))
        conn.commit()
    
        return render_template('proportional_representation_with_threshold.html',
                               party_results=party_results,
                               seats_results=seats_results,
                               vote_percentages=vote_percentages,
                               total_votes=total_votes,
                               total_valid_votes=total_votes - disqualified_votes, 
                               total_seats=total_seats,
                               party_with_most_seats=party_with_most_seats,
                               most_seats=most_seats,
                               vote_seat_differences=vote_seat_differences,
                               seat_differences_from_winner=seat_differences_from_winner)


















if __name__ == '__main__':
    app.run(debug=True)
