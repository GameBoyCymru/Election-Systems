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
        
        return render_template('first_past_the_post.html', party_results=party_results, seats_results=seats_results, vote_percentages=vote_percentages, total_votes=total_votes, total_seats=total_seats, party_with_most_seats=party_with_most_seats, most_seats=most_seats, vote_seat_differences=vote_seat_differences, seat_differences_from_winner=seat_differences_from_winner)
























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




















































# Route for the "Proportional Representation with Threshold" page
@app.route('/proportional_representation_with_threshold')
def proportional_representation_with_threshold():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()

        # Get the overall total votes
        cur.execute("SELECT SUM(votes) FROM CANDIDATE_TABLE")
        overall_total_votes = cur.fetchone()[0]

        # Calculate the threshold (5% of overall total votes)
        threshold = 0.05 * overall_total_votes

        # SQL query to fetch party name and total votes for each constituency
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
        all_parties = cur.fetchall()

        # Identify parties that are disqualified due to the threshold
        disqualified_parties = [party[0] for party in all_parties if party[1] < threshold]

        # Deduct votes of disqualified parties from overall total votes
        adjusted_total_votes = overall_total_votes - sum(party[1] for party in all_parties if party[0] in disqualified_parties)

        # SQL query to fetch party_id, party_name, total_votes, and proportional seats based on the adjusted total votes
        cur.execute("""
            SELECT
                c.party_id,
                p.name AS party_name,
                SUM(c.votes) AS total_votes,
                CAST(ROUND((SUM(c.votes) * 1.0 / ?) * ?, 0) AS INTEGER) AS proportional_seats
            FROM
                CANDIDATE_TABLE c
            JOIN
                PARTY_TABLE p ON c.party_id = p.party_id
            GROUP BY
                c.party_id
            HAVING
                party_name NOT IN ({})
            ORDER BY
                proportional_seats DESC
        """.format(','.join('?' for _ in disqualified_parties)), (adjusted_total_votes, len(constituency_data), *disqualified_parties))
        party_results = cur.fetchall()


    return render_template('proportional_representation_with_threshold.html', party_results=party_results)



if __name__ == '__main__':
    app.run(debug=True)
