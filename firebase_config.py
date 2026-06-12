import firebase_admin
from firebase_admin import credentials, firestore
from dotenv import load_dotenv
import os
import requests

load_dotenv()

# ─── Firebase Admin SDK initialize ───────────────────────────────────────────
def init_firebase():
    if not firebase_admin._apps:
        import streamlit as st
        if hasattr(st, 'secrets') and 'firebase_key' in st.secrets:
            key_dict = dict(st.secrets["firebase_key"])
            if 'private_key' in key_dict:
                key_dict['private_key'] = key_dict['private_key'].replace('\\n', '\n')
            cred = credentials.Certificate(key_dict)
        else:
            key_path = os.getenv("FIREBASE_KEY_PATH", "firebase-key.json")
            cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)
    return firestore.client()

# ─── Firestore client ─────────────────────────────────────────────────────────
db = None

def get_db():
    global db
    if db is None:
        db = init_firebase()
    return db

# ─── AUTH: Signup ─────────────────────────────────────────────────────────────
def signup_user(email, password, display_name):
    try:
        api_key = os.getenv("FIREBASE_API_KEY")
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signUp?key={api_key}"
        payload = {
            "email": email,
            "password": password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)
        data = response.json()

        if "error" in data:
            error_msg = data["error"]["message"]
            if "EMAIL_EXISTS" in error_msg:
                return False, "EMAIL_EXISTS"
            elif "WEAK_PASSWORD" in error_msg:
                return False, "WEAK_PASSWORD"
            elif "INVALID_EMAIL" in error_msg:
                return False, "INVALID_EMAIL"
            else:
                return False, error_msg

        uid      = data["localId"]
        id_token = data["idToken"]

        # ── Send verification email immediately ───────────────────────────────
        verify_url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
        requests.post(verify_url, json={
            "requestType": "VERIFY_EMAIL",
            "idToken": id_token
        })

        # ── Save user to Firestore (email_verified = False) ───────────────────
        database = get_db()
        database.collection("users").document(uid).set({
            "email":          email,
            "display_name":   display_name,
            "total_score":    0,
            "quizzes_taken":  0,
            "email_verified": False,
            "created_at":     firestore.SERVER_TIMESTAMP
        })

        return True, {
            "uid":          uid,
            "email":        email,
            "display_name": display_name,
            "token":        id_token
        }

    except Exception as e:
        return False, str(e)

# ─── AUTH: Login ──────────────────────────────────────────────────────────────
def login_user(email, password):
    try:
        api_key = os.getenv("FIREBASE_API_KEY")

        # Step 1: Sign in
        signin_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        payload = {
            "email":             email,
            "password":          password,
            "returnSecureToken": True
        }
        response = requests.post(signin_url, json=payload)
        data     = response.json()

        if "error" in data:
            error_msg = data["error"]["message"]
            if "INVALID_LOGIN_CREDENTIALS" in error_msg or \
               "INVALID_PASSWORD" in error_msg:
                return False, "INVALID_LOGIN_CREDENTIALS"
            elif "EMAIL_NOT_FOUND" in error_msg:
                return False, "EMAIL_NOT_FOUND"
            elif "INVALID_EMAIL" in error_msg:
                return False, "INVALID_EMAIL"
            elif "TOO_MANY_ATTEMPTS_TRY_LATER" in error_msg:
                return False, "TOO_MANY_ATTEMPTS"
            elif "USER_DISABLED" in error_msg:
                return False, "USER_DISABLED"
            else:
                return False, error_msg

        uid      = data["localId"]
        id_token = data["idToken"]

        # Step 2: Reload user record to get latest email_verified status
        lookup_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}"
        lookup_res = requests.post(lookup_url, json={"idToken": id_token})
        lookup_data = lookup_res.json()

        email_verified = False
        if "users" in lookup_data:
            email_verified = lookup_data["users"][0].get("emailVerified", False)

        # Step 3: Block login if not verified
        if not email_verified:
            return False, "EMAIL_NOT_VERIFIED", id_token

        # Step 4: Update Firestore email_verified field
        database = get_db()
        user_ref = database.collection("users").document(uid)
        user_ref.update({"email_verified": True})

        # Step 5: Get display name
        user_doc     = user_ref.get()
        display_name = email.split("@")[0]
        if user_doc.exists:
            display_name = user_doc.to_dict().get("display_name", display_name)

        return True, {
            "uid":          uid,
            "email":        email,
            "display_name": display_name,
            "token":        id_token
        }

    except Exception as e:
        return False, str(e)

# ─── Save quiz result ─────────────────────────────────────────────────────────
def save_quiz_result(uid, category, score, total, wrong_answers):
    try:
        database = get_db()

        # Wrong answers ko serializable format mein convert karo
        clean_wrong = []
        for w in wrong_answers:
            clean_wrong.append({
                "question": w.get("question", ""),
                "selected": w.get("selected", 0),
                "correct": w.get("correct", 0),
                "options": w.get("options", []),
                "fact": w.get("fact", "")
            })

        database.collection("quiz_results").add({
            "uid": uid,
            "category": category,
            "score": score,
            "total": total,
            "percentage": round((score / total) * 100, 1) if total > 0 else 0,
            "wrong_answers": clean_wrong,
            "timestamp": firestore.SERVER_TIMESTAMP
        })

        # User ka total score update karo
        user_ref = database.collection("users").document(uid)
        user_ref.update({
            "total_score": firestore.Increment(score),
            "quizzes_taken": firestore.Increment(1)
        })
        return True

    except Exception as e:
        print(f"Save result error: {e}")
        return False

# ─── Get leaderboard ──────────────────────────────────────────────────────────
def get_leaderboard(limit=10):
    try:
        database = get_db()
        users = database.collection("users") \
            .order_by("total_score", direction=firestore.Query.DESCENDING) \
            .limit(limit) \
            .stream()

        leaderboard = []
        for i, user in enumerate(users):
            data = user.to_dict()
            leaderboard.append({
                "rank": i + 1,
                "name": data.get("display_name", "Anonymous"),
                "score": data.get("total_score", 0),
                "quizzes": data.get("quizzes_taken", 0),
                "email": data.get("email", "")
            })
        return leaderboard

    except Exception as e:
        print(f"Leaderboard error: {e}")
        return []

# ─── Get user profile ─────────────────────────────────────────────────────────
def get_user_profile(uid):
    try:
        database = get_db()
        doc = database.collection("users").document(uid).get()
        if doc.exists:
            return doc.to_dict()
        return None
    except Exception as e:
        return None

# ─── Get user quiz history ────────────────────────────────────────────────────
def get_user_history(uid, limit=5):
    try:
        database = get_db()
        results = database.collection("quiz_results") \
            .where("uid", "==", uid) \
            .order_by("timestamp", direction=firestore.Query.DESCENDING) \
            .limit(limit) \
            .stream()
        return [r.to_dict() for r in results]
    except Exception as e:
        return []
    

    # ─── Forgot Password ──────────────────────────────────────────────────────────
def send_password_reset(email):
    try:
        api_key = os.getenv("FIREBASE_API_KEY")
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
        payload = {
            "requestType": "PASSWORD_RESET",
            "email": email
        }
        response = requests.post(url, json=payload)
        data = response.json()

        if "error" in data:
            error_msg = data["error"]["message"]
            if "EMAIL_NOT_FOUND" in error_msg:
                return False, "EMAIL_NOT_FOUND"
            elif "INVALID_EMAIL" in error_msg:
                return False, "INVALID_EMAIL"
            else:
                return False, error_msg
        return True, "Reset email sent successfully"

    except Exception as e:
        return False, str(e)

# ─── Send Email Verification ──────────────────────────────────────────────────
def send_verification_email(id_token):
    try:
        api_key = os.getenv("FIREBASE_API_KEY")
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:sendOobCode?key={api_key}"
        payload = {
            "requestType": "VERIFY_EMAIL",
            "idToken": id_token
        }
        response = requests.post(url, json=payload)
        data = response.json()

        if "error" in data:
            return False, data["error"]["message"]
        return True, "Verification email sent"

    except Exception as e:
        return False, str(e)

# ─── Check Email Verified ─────────────────────────────────────────────────────
def check_email_verified(id_token):
    try:
        api_key = os.getenv("FIREBASE_API_KEY")
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={api_key}"
        payload = {"idToken": id_token}
        response = requests.post(url, json=payload)
        data = response.json()

        if "error" in data:
            return False
        users = data.get("users", [])
        if users:
            return users[0].get("emailVerified", False)
        return False

    except Exception as e:
        return False