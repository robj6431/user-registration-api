from flask import Flask, request, jsonify

app = Flask(__name__)

# In-memory user storage
users = []

@app.route('/register', methods=['POST'])
def register_user():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    # Simulate user storage
    users.append({"email": email, "password": password})
    print(users)
    return jsonify({"message": "User registered successfully!"}), 201

if __name__ == '__main__':
    app.run(debug=True)
