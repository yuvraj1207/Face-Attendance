import os
import cv2
import json
import face_recognition
from flask import Flask, render_template, redirect, url_for, session, flash
from db import get_db_connection

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Temporary folder for login captures
os.makedirs("temp_login", exist_ok=True)

# ---------------- CAMERA UTILITIES ----------------
WORKING_CAMERA = None

def get_camera():
    """Detect a working camera automatically."""
    global WORKING_CAMERA
    if WORKING_CAMERA:
        cap = cv2.VideoCapture(*WORKING_CAMERA)
        if cap.isOpened():
            return cap

    for index in range(5):
        for backend in [cv2.CAP_DSHOW, cv2.CAP_MSMF]:
            cap = cv2.VideoCapture(index, backend)
            if cap.isOpened():
                ret, _ = cap.read()
                if ret:
                    WORKING_CAMERA = (index, backend)
                    return cap
            cap.release()
    return None

def capture_face_image():
    """Captures a face from webcam and saves to temp_login."""
    cap = get_camera()
    if not cap:
        return None

    temp_path = os.path.join("temp_login", "capture.jpg")
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame = cv2.flip(frame, 1)
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = face_recognition.face_locations(rgb_frame)

        for (top, right, bottom, left) in faces:
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

        cv2.putText(frame, "Press SPACE to capture | ESC to cancel",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.imshow("Capture Face", frame)
        key = cv2.waitKey(1) & 0xFF

        if key == 27:  # ESC
            cap.release()
            cv2.destroyAllWindows()
            return None
        elif key == 32:  # SPACE
            if faces:
                cv2.imwrite(temp_path, frame)
                cap.release()
                cv2.destroyAllWindows()
                return temp_path
    cap.release()
    cv2.destroyAllWindows()
    return None

def extract_face_encoding(image_path):
    """Returns the first face encoding found in the image."""
    img = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(img)
    return encodings[0] if encodings else None

# ---------------- ROUTES ----------------
@app.route("/")
def home():
    return redirect(url_for("login"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if session.get("user"):
        return redirect(url_for("dashboard"))

    from flask import request
    if request.method == "POST":
        full_name = request.form.get("full_name", "").strip()
        username = request.form.get("username", "").strip()

        if not full_name or not username:
            flash("All fields are required.", "danger")
            return render_template("signup.html")

        img_path = capture_face_image()
        if not img_path:
            flash("Face capture failed.", "danger")
            return render_template("signup.html")

        encoding = extract_face_encoding(img_path)
        if encoding is None:
            flash("No face detected. Try again.", "danger")
            return render_template("signup.html")

        conn = get_db_connection()
        if not conn:
            flash("Database connection failed.", "danger")
            return render_template("signup.html")

        try:
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO users (full_name, username, encoding) VALUES (%s,%s,%s)",
                (full_name, username, json.dumps(encoding.tolist()))
            )
            conn.commit()
            cur.close()
            conn.close()
            flash(f"User {full_name} registered successfully!", "success")
            return redirect(url_for("login"))
        except Exception as e:
            print("DB Insert Error:", e)
            flash("Username already exists or DB error.", "danger")
            return render_template("signup.html")

    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("user"):
        return redirect(url_for("dashboard"))

    from flask import request
    if request.method == "POST":
        img_path = capture_face_image()
        if not img_path:
            flash("Could not access camera.", "danger")
            return render_template("login.html")

        encoding = extract_face_encoding(img_path)
        if encoding is None:
            flash("No face detected. Try again.", "danger")
            return render_template("login.html")

        # Fetch all users from DB
        conn = get_db_connection()
        if not conn:
            flash("Database connection failed.", "danger")
            return render_template("login.html")
        try:
            cur = conn.cursor()
            cur.execute("SELECT full_name, username, encoding FROM users")
            rows = cur.fetchall()
            cur.close()
            conn.close()
        except Exception as e:
            print("DB Fetch Error:", e)
            flash("Database fetch error.", "danger")
            return render_template("login.html")

        # Compare captured face with all user encodings
        for full_name, username, encoding_blob in rows:
            db_encoding = json.loads(encoding_blob)
            match = face_recognition.compare_faces([db_encoding], encoding)[0]
            distance = face_recognition.face_distance([db_encoding], encoding)[0]
            if match and distance < 0.4:
                session["user"] = f"{full_name} ({username})"
                flash(f"Welcome, {full_name}!", "success")
                return redirect(url_for("dashboard"))

        flash("Face not recognized. Try again or sign up.", "danger")
        return render_template("login.html")

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template("dashboard.html", user=session["user"])

@app.route("/logout")
def logout():
    session.pop("user", None)
    flash("Logged out successfully.", "info")
    return redirect(url_for("login"))

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app.run(debug=True)
