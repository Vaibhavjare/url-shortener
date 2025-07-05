from flask import Flask, render_template, request, redirect
import mysql.connector, string, random

# Initialize the Flask app
app = Flask(__name__)

# Connect to MySQL database
def get_db():
    return mysql.connector.connect(
        host="localhost",               # Database host
        user="root",                    # Your MySQL username
        password="Indra#123",           # Your MySQL password
        database="url_shortener"         # Database name
    )

# Generate a random short code (default length = 6)
def gen_code(length=6):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Home route: handles form submission and displays shortened link
@app.route("/", methods=["GET", "POST"])
def index():
    short = None  # Will hold the final short code to display
    if request.method == "POST":
        # Get form data from user
        original = request.form.get("url", "").strip()
        custom = request.form.get("custom", "").strip()
        name = request.form.get("name", "").strip()

        # Ensure all fields are filled
        if not original or not custom or not name:
            return "❌ All fields (URL, custom code, name) are required!"

        # Add https:// if not already present in the URL
        if not original.startswith("http://") and not original.startswith("https://"):
            original = "https://" + original

        # Insert the record into database
        conn = get_db()
        cur = conn.cursor()
        try:
            cur.execute(
                "INSERT INTO urls (original_url, short_code, name) VALUES (%s, %s, %s)",
                (original, custom, name)
            )
            conn.commit()
            short = custom  # Display custom code if successful
        except mysql.connector.errors.IntegrityError:
            return "❌ That custom code already exists. Try another."

    return render_template("index.html", short=short)

# This route handles redirecting short URL to the original one
@app.route("/<code>")
def redirect_code(code):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT original_url FROM urls WHERE short_code=%s", (code,))
    result = cur.fetchone()
    if result:
        return redirect(result[0])  # Redirect if found
    return "❌ Short URL not found", 404  # Show 404 if not found

# Run the Flask application
if __name__ == "__main__":
    print("✅ Flask app running at http://127.0.0.1:5000/")
    app.run(debug=True)