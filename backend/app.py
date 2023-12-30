import sqlite3
from flask import Flask, jsonify, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

con = sqlite3.connect('myZoo.db', check_same_thread=False)
cur = con.cursor()
try:
    cur.execute('CREATE TABLE users(username TEXT, password TEXT, first_name TEXT, last_name TEXT)')
    cur.execute('CREATE TABLE animals(name TEXT, species TEXT, num_of_legs INTEGER, id INTEGER PRIMARY KEY AUTOINCREMENT)')
except:
    pass

# Function to add user data to the database
def add_user_to_db(username, password, first_name, last_name):
    cur.execute("INSERT INTO users (username, password, first_name, last_name) VALUES (?, ?, ?, ?)",
                    (username, password, first_name, last_name))
    con.commit()
    
    


logged_in = False


@app.route("/", methods=["post"])
def main():
    global logged_in
    data = request.get_json()
    cur.execute('SELECT * FROM users WHERE username= ? AND password= ?', (data["username"], data["password"]))
    user = cur.fetchone() 

    if user:
        logged_in =True
        return jsonify(message="Logged In"), 200
    else:
        return jsonify(message="Username or Password ar incorrect"), 401


@app.route("/register", methods=['POST'])
def register():
    data = request.get_json()
    username = data['username']
    password = data['password']
    first_name = data['fName']
    last_name = data['lName']
    print(username, password, first_name, last_name)
    cur.execute("INSERT INTO users (username, password, first_name, last_name) VALUES (?, ?, ?, ?)",
                   (username, password, first_name, last_name))
    con.commit()
    return jsonify(message="user added successfuly"), 200


# Route to display the Zoo page
@app.route("/zoo", methods=['GET'])
def zoo():
    # Check if the user is logged in
    if not logged_in:
        return jsonify(message="Unauthorized. Please log in to access the Zoo.")

    cur.execute('SELECT id, name, species, num_of_legs FROM animals')
    animals = cur.fetchall()  # Fetch all animal records
    animal_list = [{'id': animal[0], 'name': animal[1], 'species': animal[2], 'num_of_legs': animal[3]} for animal in animals]

    return jsonify(animals=animal_list)  # Return JSON response with animal data using 'animals' key


@app.route("/add_animal", methods= ['POST'])
def add_animal():
    data = request.get_json()
    name = data['name']
    species = data['species']
    legs = data['legs']
    cur.execute('INSERT INTO animals (name, species, num_of_legs) VALUES (?, ?, ?)', (name, species, legs))
    con.commit()

    return jsonify(message= "car added successfully")

@app.route("/delete_animal/<int:animal_id>", methods=['DELETE'])
def delete_animal(animal_id):
    print("in")
    try:
        cur.execute('DELETE FROM animals WHERE id = ?', (animal_id,))
        con.commit()
        return jsonify(message=f"Animal with ID {animal_id} deleted successfully")
    except Exception as e:
        return jsonify(message="Failed to delete the animal", error=str(e))

@app.route("/update_animal/<int:animal_id>", methods=['PUT'])
def update_animal(animal_id):
    try:
        data = request.get_json()
        name = data['name']
        species = data['species']
        legs = data['legs']

        cur.execute('UPDATE animals SET name=?, species=?, num_of_legs=? WHERE id=?',
                    (name, species, legs, animal_id))
        con.commit()

        return jsonify(message=f"Animal with ID {animal_id} updated successfully")
    except Exception as e:
        return jsonify(message="Failed to update the animal", error=str(e))

if __name__ == "__main__":
    app.run(debug=True)