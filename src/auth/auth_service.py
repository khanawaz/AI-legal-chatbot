from typing import Optional, Tuple
from .supabase_client import supabase

def signup_email_password(email: str, password: str, full_name: str = "") -> Tuple[bool, str]:
    try:
        sb = supabase()
        sb.auth.sign_up({"email": email, "password": password})

        # Try to create a profiles row if we can resolve the user
        user_id = None
        try:
            sess = sb.auth.get_session()
            if sess and getattr(sess, "user", None):
                user_id = sess.user.id
        except Exception:
            pass
        if not user_id:
            try:
                u = sb.auth.get_user()
                if u and getattr(u, "user", None):
                    user_id = u.user.id
            except Exception:
                pass
        if user_id and full_name:
            try:
                sb.table("profiles").insert({"id": user_id, "full_name": full_name}).execute()
            except Exception:
                pass

        return True, "Signup successful. Check your email if confirmations are enabled."
    except Exception as e:
        return False, f"Signup error: {e}"

def login_email_password(email: str, password: str):
    sb = supabase()
    return sb.auth.sign_in_with_password({"email": email, "password": password})

def logout():
    try:
        supabase().auth.sign_out()
    except Exception:
        pass

def current_user() -> Optional[dict]:
    try:
        sess = supabase().auth.get_session()
        user = getattr(sess, "user", None) if sess else None
        if user:
            return {"id": getattr(user, "id", None), "email": getattr(user, "email", None)}
    except Exception:
        pass
    return None
