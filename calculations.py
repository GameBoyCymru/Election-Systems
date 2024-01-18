from flask import Flask, render_template
import sqlite3
import math
import random
import os

app = Flask(__name__) 




# check if the database exists. If it does not, run the create_tables script to create the database
if not os.path.exists('database.db'):
    import create_tables



actual_election_winner = "Conservative"     # The actual winner of the election

# Function to insert results from each election system into the RESULTS_TABLE
def insert_into_results_table(election_system_name, name, votes, seats, vote_percentages, seat_percentages,vote_seat_differences, seat_differences_from_winner, is_different_from_winner, total_valid_votes, party_with_most_seats):
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO RESULTS_TABLE (election_system_name, name, votes, seats, vote_percentages, seat_percentages, vote_seat_differences, seat_differences_from_winner, is_different_from_winner, total_valid_votes, party_with_most_seats)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (election_system_name, name, votes, seats, vote_percentages, seat_percentages, vote_seat_differences, seat_differences_from_winner, is_different_from_winner, total_valid_votes, party_with_most_seats))

#  Runs the first past the post election system and inserts the results into the database
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
        seat_differences_from_winner = {}
        for party_name in seats_results.keys():
            party_seats = seats_results.get(party_name, 0)
            difference = party_seats - most_seats
            seat_differences_from_winner[party_name] = difference
        
        is_different_from_winner = 'No' if party_with_most_seats == actual_election_winner else 'Yes'
        election_system_name = "First Past the Post"
        total_valid_votes = total_votes


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

# Runs the simple proportional representation (with and without the threshold) election system and inserts the results into the database
def simple_proportional_representation(election_system_name, disqualified_threshold=0):
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
        vote_percentages = {}

        disqualified_votes = 0
        disqualified_parties = []

        # Disqualify parties with less than the specified threshold
        for party_name, total_votes_party in party_results[:]:
            vote_percentage = (total_votes_party / total_votes) * 100

            if vote_percentage < disqualified_threshold:
                disqualified_votes += total_votes_party
                disqualified_parties.append(party_name)
                seats_results[party_name] = 0
                vote_percentages[party_name] = 0.00
                party_results.remove((party_name, total_votes_party))

        # Calculate the seat count for the remaining parties
        for party_name, total_votes_party in party_results:
            if party_name not in disqualified_parties:
                seat_count = round((total_votes_party / (total_votes - disqualified_votes)) * total_seats)
                seats_results[party_name] = seat_count

        # Add parties without seats to the seats_results with default value 0
        for party_name, _ in party_results:
            seats_results.setdefault(party_name, 0)

        # Calculate the percentage of votes for each party
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
        seat_differences_from_winner = {}
        for party_name in seats_results.keys():
            party_seats = seats_results.get(party_name, 0)
            difference = party_seats - most_seats
            seat_differences_from_winner[party_name] = difference

        is_different_from_winner = 'No' if party_with_most_seats == actual_election_winner else 'Yes'
        total_valid_votes = total_votes - disqualified_votes

        # Insert the results into the database
        for party_name in sorted(seats_results.keys()):
            votes = dict(party_results).get(party_name, 0)
            seats = seats_results.get(party_name, 0)
            vote_percentage = vote_percentages.get(party_name, 0)
            seat_percentage = (seats_results.get(party_name, 0) / total_seats) * 100
            vote_seat_difference = vote_seat_differences.get(party_name, 0)
            seat_difference_from_winner = seat_differences_from_winner.get(party_name, 0)

            insert_into_results_table(election_system_name, party_name, votes, seats, vote_percentage,
                                      seat_percentage, vote_seat_difference, seat_difference_from_winner,
                                      is_different_from_winner, total_valid_votes, party_with_most_seats)

        conn.commit()

# Runs the proportional representation by criteria election system and inserts the results into the database
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

        # Iterate over each criterion (county, region or country)
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

                # Calculate the seats for the party in the criterion
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
        is_different_from_winner = 'No' if party_with_most_seats == actual_election_winner else 'Yes'

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

# Runs the largest remainder by criteria election system and inserts the results into the database
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
        is_different_from_winner = 'No' if party_with_most_seats == actual_election_winner else 'Yes'

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

# Runs the d'hont by criteria election system and inserts the results into the database
def dhondt_by_criteria(criteria_name, criteria_id):
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


        # Calculate total votes and total seats for the entire election
        total_votes = sum([row[2] for row in party_results])
        total_seats = sum(party_total_seats.values())

        # Insert the results into the database
        election_system_name = f"D'Hondt by {criteria_name}"
        total_valid_votes = total_votes
        party_with_most_seats = max(party_total_seats, key=party_total_seats.get)
        is_different_from_winner = 'No' if party_with_most_seats == actual_election_winner else 'Yes'

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

# Runs the webster by criteria election system and inserts the results into the database
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


        # Calculate total votes and total seats for the entire election
        total_votes = sum([row[2] for row in party_results])
        total_seats = sum(party_total_seats.values())

        # Insert the results into the database
        election_system_name = f"Webster by {criteria_name}"
        total_valid_votes = total_votes
        party_with_most_seats = max(party_total_seats, key=party_total_seats.get)
        is_different_from_winner = 'No' if party_with_most_seats == actual_election_winner else 'Yes'

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

# Runs the custom by criteria election system and inserts the results into the database
def custom_by_criteria(criteria_name, criteria_id):
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

            # Initialize a list of parties, each with their total votes and zero seats
            parties = [{'name': party_name, 'votes': sum(row[2] for row in party_results if row[0] == party_name and row[1] == criterion_value), 'seats': 0} for party_name in set(row[0] for row in party_results if row[1] == criterion_value)]

            # Repeat until all seats are allocated
            while sum(party['seats'] for party in parties) < total_seats_for_criterion:
                # For each party, calculate the quotient
                for party in parties:
                    party['quot'] = ((party['votes'] / (2*party['seats'] + 1)) * -1) + random.randint(-100,100)


                # Allocate a seat to the party with the highest quotient
                max_quot_party = max(parties, key=lambda party: party['quot'])
                max_quot_party['seats'] += 1

            # Update the total seats for each party
            for party in parties:
                party_total_seats[party['name']] = party_total_seats.get(party['name'], 0) + party['seats']


        # Calculate total votes and total seats for the entire election
        total_votes = sum([row[2] for row in party_results])
        total_seats = sum(party_total_seats.values())

        # Insert the results into the database
        election_system_name = f"Custom by {criteria_name}"
        total_valid_votes = total_votes
        party_with_most_seats = max(party_total_seats, key=party_total_seats.get)
        is_different_from_winner = 'No' if party_with_most_seats == actual_election_winner else 'Yes'

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

def do_maths():
    first_past_the_post()
    simple_proportional_representation("Proportional Representation (All Seats)")
    simple_proportional_representation("Proportional Representation with 5% Threshold (All Seats)", disqualified_threshold=5)
    proportional_representation_by_criteria("County", "county_id")
    proportional_representation_by_criteria("Region", "region_id")
    proportional_representation_by_criteria("Country", "country_id")
    largest_remainder_by_criteria("County", "county_id")
    largest_remainder_by_criteria("Region", "region_id")
    largest_remainder_by_criteria("Country", "country_id")
    dhondt_by_criteria("County", "county_id")
    dhondt_by_criteria("Region", "region_id")
    dhondt_by_criteria("Country", "country_id")
    webster_by_criteria("County", "county_id")
    webster_by_criteria("Region", "region_id")
    webster_by_criteria("Country", "country_id")
    custom_by_criteria("County", "county_id")
    custom_by_criteria("Region", "region_id")
    custom_by_criteria("Country", "country_id")



# check if the results table exists with data. If it does not, run the do_maths function to calculate the results
with sqlite3.connect('database.db') as conn:
    cur = conn.cursor()
    cur.execute("SELECT * FROM RESULTS_TABLE")
    results = cur.fetchall()
    if not results:
        do_maths()



# Route for the main menu page
@app.route('/')
def index():
    return render_template('index.html')

# Get the results from the database and return them to the results page
def get_results_from_table(election_system_name):
    with sqlite3.connect('database.db') as conn:
        
        cur = conn.cursor()
        cur.execute("SELECT * FROM RESULTS_TABLE WHERE election_system_name = ? ORDER BY name ASC", (election_system_name,))
        rows = cur.fetchall()

        
        cur.execute("SELECT SUM(votes) FROM CANDIDATE_TABLE")
        total_votes = cur.fetchone()[0]
        
        
        # Calculate the total number of seats from the seats awarded
        total_seats = sum(row[3] for row in rows)

        # Find the seat count of the party with the most seats
        most_seats = max(row[3] for row in rows)

    return rows, total_votes, total_seats, most_seats


@app.route('/results/<election_system_name>')   # Route for the "results" page with the election system name as a parameter
def results(election_system_name):

    election_system_name = election_system_name.replace('_', ' ')   # Replace underscores with spaces
    results, total_votes, total_seats, most_seats = get_results_from_table(election_system_name)    # Get the results from the database
    return render_template('results.html', election_system_name=election_system_name, results=results, total_votes=total_votes, total_seats=total_seats, most_seats=most_seats)  # Render the results template with the results


# Route for the party details page
@app.route('/party_details/<party_name>')
def party_details(party_name):
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()

        party_name = party_name.replace('_', ' ')

        cur.execute("""
            SELECT c.name as candidate_name, g.gender_type, c.sitting, c.votes, con.name as constituency_name
            FROM CANDIDATE_TABLE c
            JOIN PARTY_TABLE p ON c.party_id = p.party_id
            JOIN GENDER_TABLE g ON c.gender_id = g.gender_id
            JOIN CONSTITUENCY_TABLE con ON c.constituency_id = con.constituency_id
            WHERE p.name = ?
        """, (party_name,))

        party_candidates = cur.fetchall()

        # Calculate total votes for the party
        total_votes = sum(candidate[3] for candidate in party_candidates)

        return render_template('party_details.html',
                               party_name=party_name,
                               party_candidates=party_candidates,
                               total_votes=total_votes)


@app.route('/candidate_details/<candidate_name>')
def candidate_details(candidate_name):
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()

        candidate_name = candidate_name.replace('_', ' ')

        # Retrieve candidate details from the database
        cur.execute("""
                SELECT c.name as candidate_name, g.gender_type as gender, c.sitting, c.votes,
                       con.name as constituency_name, con.type as constituency_type,
                       co.name as county_name, reg.name as region_name, cou.name as country_name
                FROM CANDIDATE_TABLE c
                JOIN GENDER_TABLE g ON c.gender_id = g.gender_id
                JOIN CONSTITUENCY_TABLE con ON c.constituency_id = con.constituency_id
                JOIN COUNTY_TABLE co ON c.county_id = co.county_id
                JOIN REGION_TABLE reg ON c.region_id = reg.region_id
                JOIN COUNTRY_TABLE cou ON c.country_id = cou.country_id
                WHERE c.name = ?
            """, (candidate_name,))

        candidate_details = cur.fetchone()

    return render_template('candidate_details.html', candidate_details=candidate_details)


if __name__ == '__main__':
    app.run(debug=True) # Run the Flask app in debug mode