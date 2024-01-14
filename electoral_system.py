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


#drops table RESULTS_TABLE if exists
cur.execute("DROP TABLE IF EXISTS DEBUG_TABLE")
#runs create table script
cur.execute("""
            CREATE TABLE DEBUG_TABLE (
                id integer,
                name TEXT,
                total_seats INTEGER,
                seats_awarded INTEGER
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
        total_valid_votes = total_votes
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
                seat_count = (total_votes_party / total_votes) * total_seats
                seats_results[party_name] = seat_count
            else:
                seats_results[party_name] = 0

        # Add parties without seats to the seats_results with default value 0
        for party_name, _ in party_results:
            seats_results.setdefault(party_name, 0)

        # If total allocated seats exceed the limit, scale down the seats proportionally
        total_allocated_seats = sum(seats_results.values())
        if total_allocated_seats > 650:
            scale_factor = 650 / total_allocated_seats
            seats_results = {party_name: math.ceil(seats * scale_factor) for party_name, seats in seats_results.items()}
        # scale it up if it is less than 650
        elif total_allocated_seats < 650:
            scale_factor = 650 / total_allocated_seats
            seats_results = {party_name: round(seats * scale_factor) for party_name, seats in seats_results.items()}





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
        election_system_name = "Proportional Representation (All Seats)"
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

        # If total allocated seats exceed the limit, scale down the seats proportionally
        total_allocated_seats = sum(seats_results.values())
        if total_allocated_seats > 650:
            scale_factor = 650 / total_allocated_seats
            seats_results = {party_name: math.ceil(seats * scale_factor) for party_name, seats in seats_results.items()}
        # scale it up if it is less than 650
        elif total_allocated_seats < 650:
            scale_factor = 650 / total_allocated_seats
            seats_results = {party_name: round(seats * scale_factor) for party_name, seats in seats_results.items()}



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
        election_system_name = "Proportional Representation with 5% Threshold (All Seats)"
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

def proportional_representation_by_criteria(criteria_name, criteria_id):
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()

        # Get the total number of seats
        cur.execute("SELECT COUNT(DISTINCT constituency_id) FROM CANDIDATE_TABLE")
        total_seats = cur.fetchone()[0]

        # Fetch party results grouped by the specified criteria
        cur.execute(f"""
            SELECT
                p.name AS party_name,
                c.{criteria_id},
                SUM(c.votes) AS total_party_votes,
                (SELECT COUNT(DISTINCT constituency_id) FROM CANDIDATE_TABLE WHERE {criteria_id} = c.{criteria_id}) AS {criteria_name}_total_seats
            FROM
                CANDIDATE_TABLE c
            JOIN
                PARTY_TABLE p ON c.party_id = p.party_id
            GROUP BY
                c.party_id, c.{criteria_id}
        """)

        party_results_by_criteria = cur.fetchall()

        # Initialize a dictionary to store the total seats for each party
        party_total_seats = {}

        # Iterate over each criterion
        for criterion_value in set(row[1] for row in party_results_by_criteria):
            # Calculate the total seats based on the number of constituencies for the current criterion
            cur.execute(f"SELECT COUNT(DISTINCT constituency_id) FROM CANDIDATE_TABLE WHERE {criteria_id} = ?", (criterion_value,))
            criterion_total_seats = cur.fetchone()[0]

            # Calculate the total votes in the criterion
            criterion_total_votes = sum(row[2] for row in party_results_by_criteria if row[1] == criterion_value)

            for party_name in set(row[0] for row in party_results_by_criteria if row[1] == criterion_value):
                # Get the total votes for the party in the criterion
                party_total_votes = sum(row[2] for row in party_results_by_criteria if row[0] == party_name and row[1] == criterion_value)

                # Calculate the proportion of seats for the party in the criterion
                proportion_in_criterion = party_total_votes / criterion_total_votes

                # Calculate the seats for the party in the criterion (rounded to the nearest integer)
                seats_in_criterion = proportion_in_criterion * criterion_total_seats

                # Update the total seats for the party
                party_total_seats[party_name] = round(party_total_seats.get(party_name, 0) + seats_in_criterion)

        # Calculate total votes and total seats for the entire election
        total_votes = sum([row[2] for row in party_results_by_criteria])
        total_seats = sum(party_total_seats.values())

        # Insert the results into the database
        election_system_name = f"Proportional Representation by {criteria_name}"
        total_valid_votes = total_votes
        party_with_most_seats = max(party_total_seats, key=party_total_seats.get)
        is_different_from_winner = 'No' if party_with_most_seats == 'Conservative' else 'Yes'

        for party_name, seats in party_total_seats.items():
            votes = sum([row[2] for row in party_results_by_criteria if row[0] == party_name])
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

def largest_remainder_by_criteria(criteria_name, criteria_id):
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()

        # Get the total number of seats
        cur.execute("SELECT COUNT(DISTINCT constituency_id) FROM CANDIDATE_TABLE")
        total_seats = cur.fetchone()[0]

        # Fetch party results grouped by the specified criteria
        cur.execute(f"""
                    SELECT
                        p.name AS party_name,
                        c.{criteria_id},
                        SUM(c.votes) AS total_party_votes,
                        (SELECT COUNT(DISTINCT constituency_id) FROM CANDIDATE_TABLE WHERE {criteria_id} = c.{criteria_id}) AS {criteria_name}_total_seats
                    FROM
                        CANDIDATE_TABLE c
                    JOIN
                        PARTY_TABLE p ON c.party_id = p.party_id
                    GROUP BY
                        c.party_id, c.{criteria_id}
                """)

        party_results_by_criteria = cur.fetchall()

        # Initialize a dictionary to store the total seats for each party
        party_total_seats = {}

        # Iterate over each criterion
        for criterion_value in set(row[1] for row in party_results_by_criteria):

            # Calculate the total seats based on the number of constituencies for the current criterion
            cur.execute(f"SELECT COUNT(DISTINCT constituency_id) FROM CANDIDATE_TABLE WHERE {criteria_id} = ?", (criterion_value,))
            criterion_total_seats = cur.fetchone()[0]

            # Calculate the total votes in the criterion
            criterion_total_votes = sum(row[2] for row in party_results_by_criteria if row[1] == criterion_value)

            hare_quota = criterion_total_votes / criterion_total_seats

            # Iterate over each party in the criterion
            seats_awarded = 0

            for party_name in set(row[0] for row in party_results_by_criteria if row[1] == criterion_value):
                # Get the total votes for the party in the criterion
                party_total_votes = sum(row[2] for row in party_results_by_criteria if row[0] == party_name and row[1] == criterion_value)

                # Calculate the seats for the party in the criterion
                party_total_seats[party_name] = math.floor(party_total_seats.get(party_name, 0) + (party_total_votes / hare_quota))

                # Add the seats awarded to the total seats awarded
                seats_awarded += math.floor(party_total_votes / hare_quota)

            # Sort the party_total_seats dictionary by seats in descending order
            sorted_seats = sorted(party_total_seats.items(), key=lambda x: x[1], reverse=True)

            while seats_awarded < criterion_total_seats:
                # Loop through the sorted_seats list and add 1 seat to each party until the total seats awarded is equal to the total seats in the criterion
                for party_name, seats in sorted_seats:
                    if seats_awarded < criterion_total_seats:
                        party_total_seats[party_name] += 1
                        seats_awarded += 1
                    else:
                        break

        # Calculate total votes and total seats for the entire election
        total_votes = sum([row[2] for row in party_results_by_criteria])
        total_seats = sum(party_total_seats.values())

        # Insert the results into the database
        election_system_name = f"Largest Remainder by {criteria_name}"
        total_valid_votes = total_votes
        party_with_most_seats = max(party_total_seats, key=party_total_seats.get)
        is_different_from_winner = 'No' if party_with_most_seats == 'Conservative' else 'Yes'

        for party_name, seats in party_total_seats.items():
            votes = sum([row[2] for row in party_results_by_criteria if row[0] == party_name])
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

def dhont_by_criteria(criteria_name, criteria_id):
    with (sqlite3.connect('database.db') as conn):
        cur = conn.cursor()

        # Get the total number of seats
        cur.execute("SELECT COUNT(DISTINCT constituency_id) FROM CANDIDATE_TABLE")
        total_seats = cur.fetchone()[0]

        # Fetch party results grouped by the specified criteria
        cur.execute(f"""
                    SELECT
                        p.name AS party_name,
                        c.{criteria_id},
                        SUM(c.votes) AS total_party_votes,
                        COUNT(DISTINCT c.constituency_id) AS total_seats
                    FROM
                        CANDIDATE_TABLE c
                    JOIN
                        PARTY_TABLE p ON c.party_id = p.party_id
                    GROUP BY
                        c.party_id, c.{criteria_id}
                """)

        party_results = cur.fetchall()

        # Initialize a dictionary to store the total seats for each party
        party_total_seats = {}

        # Iterate over each criterion
        for criterion_value in set(row[1] for row in party_results):

            # Calculate the total seats based on the number of constituencies for the current criterion
            cur.execute(f"SELECT COUNT(DISTINCT constituency_id) FROM CANDIDATE_TABLE WHERE {criteria_id} = ?", (criterion_value,))
            total_seats_for_criterion = cur.fetchone()[0]

            # Get the name of the criterion (e.g., county_name, region_name, country_name)
            criterion_name = criterion_value  # Assuming criterion_value itself is the name

            # Initialize a list of parties, each with their total votes and zero seats
            parties = [{'name': party_name, 'votes': sum(row[2] for row in party_results if row[0] == party_name and row[1] == criterion_value), 'seats': 0} for party_name in set(row[0] for row in party_results if row[1] == criterion_value)]

            # Repeat until all seats are allocated
            while sum(party['seats'] for party in parties) < total_seats_for_criterion:
                # For each party, calculate the quotient
                for party in parties:
                    party['quot'] = party['votes'] / (party['seats'] + 1)

                # Allocate a seat to the party with the highest quotient
                max_quot_party = max(parties, key=lambda party: party['quot'])
                max_quot_party['seats'] += 1

            # Update the total seats for each party
            for party in parties:
                party_total_seats[party['name']] = party_total_seats.get(party['name'], 0) + party['seats']

            # insert the id, criterion name, and total seats into the debug table
            cur.execute("INSERT INTO DEBUG_TABLE (id, name, total_seats, seats_awarded) VALUES (?, ?, ?, ?)", (criterion_value, criterion_name, total_seats_for_criterion, 0))

        # Initialize a variable to store the total seats across all criteria
        all_seats = 0

        # Iterate over each unique criterion
        for criterion_value in set(row[1] for row in party_results):
            # Fetch the total seats for the criterion from the database
            cur.execute(f"SELECT COUNT(DISTINCT constituency_id) FROM CANDIDATE_TABLE WHERE {criteria_id} = ?", (criterion_value,))
            total_seats_for_criterion = cur.fetchone()[0]

            # Add the total seats for the criterion to the total seats across all criteria
            all_seats += total_seats_for_criterion

        # Sum all seats awarded
        allocated_seats =  sum(party_total_seats.values())

        # insert the total seats for all criteria into the debug table
        cur.execute("INSERT INTO DEBUG_TABLE (id, name, total_seats, seats_awarded) VALUES (?, ?, ?, ?)", (0, f"All {criteria_name}s", all_seats, allocated_seats))

        # Calculate total votes and total seats for the entire election
        total_votes = sum([row[2] for row in party_results])
        total_seats = sum(party_total_seats.values())

        # Insert the results into the database
        election_system_name = f"D'Hont by {criteria_name}"
        total_valid_votes = total_votes
        party_with_most_seats = max(party_total_seats, key=party_total_seats.get)
        is_different_from_winner = 'No' if party_with_most_seats == 'Conservative' else 'Yes'

        for party_name, seats in party_total_seats.items():
            votes = sum([row[2] for row in party_results if row[0] == party_name])
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

def webster_by_criteria(criteria_name, criteria_id):
    with (sqlite3.connect('database.db') as conn):
        cur = conn.cursor()

        # Get the total number of seats
        cur.execute("SELECT COUNT(DISTINCT constituency_id) FROM CANDIDATE_TABLE")
        total_seats = cur.fetchone()[0]

        # Fetch party results grouped by the specified criteria
        cur.execute(f"""
                    SELECT
                        p.name AS party_name,
                        c.{criteria_id},
                        SUM(c.votes) AS total_party_votes,
                        COUNT(DISTINCT c.constituency_id) AS total_seats
                    FROM
                        CANDIDATE_TABLE c
                    JOIN
                        PARTY_TABLE p ON c.party_id = p.party_id
                    GROUP BY
                        c.party_id, c.{criteria_id}
                """)

        party_results = cur.fetchall()

        # Initialize a dictionary to store the total seats for each party
        party_total_seats = {}

        # Iterate over each criterion
        for criterion_value in set(row[1] for row in party_results):

            # Calculate the total seats based on the number of constituencies for the current criterion
            cur.execute(f"SELECT COUNT(DISTINCT constituency_id) FROM CANDIDATE_TABLE WHERE {criteria_id} = ?", (criterion_value,))
            total_seats_for_criterion = cur.fetchone()[0]

            # Get the name of the criterion (e.g., county_name, region_name, country_name)
            criterion_name = criterion_value  # Assuming criterion_value itself is the name

            # Initialize a list of parties, each with their total votes and zero seats
            parties = [{'name': party_name, 'votes': sum(row[2] for row in party_results if row[0] == party_name and row[1] == criterion_value), 'seats': 0} for party_name in set(row[0] for row in party_results if row[1] == criterion_value)]

            # Repeat until all seats are allocated
            while sum(party['seats'] for party in parties) < total_seats_for_criterion:
                # For each party, calculate the quotient
                for party in parties:
                    party['quot'] = party['votes'] / (2*party['seats'] + 1)

                # Allocate a seat to the party with the highest quotient
                max_quot_party = max(parties, key=lambda party: party['quot'])
                max_quot_party['seats'] += 1

            # Update the total seats for each party
            for party in parties:
                party_total_seats[party['name']] = party_total_seats.get(party['name'], 0) + party['seats']

            # insert the id, criterion name, and total seats into the debug table
            cur.execute("INSERT INTO DEBUG_TABLE (id, name, total_seats, seats_awarded) VALUES (?, ?, ?, ?)", (criterion_value, criterion_name, total_seats_for_criterion, 0))

        # Initialize a variable to store the total seats across all criteria
        all_seats = 0

        # Iterate over each unique criterion
        for criterion_value in set(row[1] for row in party_results):
            # Fetch the total seats for the criterion from the database
            cur.execute(f"SELECT COUNT(DISTINCT constituency_id) FROM CANDIDATE_TABLE WHERE {criteria_id} = ?", (criterion_value,))
            total_seats_for_criterion = cur.fetchone()[0]

            # Add the total seats for the criterion to the total seats across all criteria
            all_seats += total_seats_for_criterion

        # Sum all seats awarded
        allocated_seats =  sum(party_total_seats.values())

        # insert the total seats for all criteria into the debug table
        cur.execute("INSERT INTO DEBUG_TABLE (id, name, total_seats, seats_awarded) VALUES (?, ?, ?, ?)", (0, f"All {criteria_name}s", all_seats, allocated_seats))

        # Calculate total votes and total seats for the entire election
        total_votes = sum([row[2] for row in party_results])
        total_seats = sum(party_total_seats.values())

        # Insert the results into the database
        election_system_name = f"Webster by {criteria_name}"
        total_valid_votes = total_votes
        party_with_most_seats = max(party_total_seats, key=party_total_seats.get)
        is_different_from_winner = 'No' if party_with_most_seats == 'Conservative' else 'Yes'

        for party_name, seats in party_total_seats.items():
            votes = sum([row[2] for row in party_results if row[0] == party_name])
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
proportional_representation_by_criteria("County", "county_id")
proportional_representation_by_criteria("Region", "region_id")
proportional_representation_by_criteria("Country", "country_id")
largest_remainder_by_criteria("County", "county_id")
largest_remainder_by_criteria("Region", "region_id")
largest_remainder_by_criteria("Country", "country_id")
dhont_by_criteria("County", "county_id")
dhont_by_criteria("Region", "region_id")
dhont_by_criteria("Country", "country_id")
webster_by_criteria("County", "county_id")
webster_by_criteria("Region", "region_id")
webster_by_criteria("Country", "country_id")


# Route for the "index" page
@app.route('/')
def index():

    return render_template('index.html')


def get_results_from_table(election_system_name):
    with sqlite3.connect('database.db') as conn:
        
        cur = conn.cursor()
        cur.execute("SELECT * FROM RESULTS_TABLE WHERE election_system_name = ? ORDER BY name ASC", (election_system_name,))
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