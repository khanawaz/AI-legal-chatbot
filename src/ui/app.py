from __future__ import annotations
import os, sys
from pathlib import Path

# --- Path/bootstrap so `src.*` imports work when launching from anywhere
PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

import chainlit as cl

# Auth helpers (Supabase-based)
from src.auth.auth_service import (
    login_email_password,
    signup_email_password,
    logout as sb_logout,
    current_user,
)

# Optional helper to resend email confirmation
try:
    from src.auth.auth_service import resend_confirmation
except Exception:
    resend_confirmation = None

from src.llm.rag_pipeline import get_legal_answer


# --------------------------- Constants & Styling ---------------------------

APP_TITLE = "⚖️ LegaBot"
APP_SUBTITLE = "Indian Legal Research Assistant"

# Message templates with better formatting
WELCOME_MSG = """# Welcome to LegaBot! ⚖️

Your intelligent assistant for Indian legal research powered by AI.

**What I can help you with:**
- 🔍 Search through Indian legal documents
- 📚 Explain legal concepts and sections
- ⚖️ Provide insights on IPC, CrPC, and other acts
- 💡 Answer your legal queries with accurate citations

Please **login** or **sign up** to get started.
"""

LOGGED_IN_MSG = """# Welcome back to LegaBot! 👋

**Ready to assist you with your legal queries.**

Ask me anything about Indian law, or try one of the example questions below.

---
*💡 Tip: Be specific in your questions for better results*
"""

EXAMPLES_MSG = """# 💡 Example Questions

Try asking questions like these:

**Criminal Law:**
- "What constitutes theft under IPC Section 378?"
- "Explain the punishment for murder under IPC"
- "What are the bail provisions in CrPC?"

**Civil Law:**
- "What is the limitation period for filing a suit?"
- "Explain property transfer laws"

**Constitutional Law:**
- "What are fundamental rights under the Constitution?"
- "Explain Article 21 - Right to Life"

Click the examples below or type your own question!
"""


# --------------------------- Session Management ---------------------------

def set_session_user(user: dict | None):
    cl.user_session.set("user", user if user else None)

def get_session_user() -> dict | None:
    u = current_user()
    if u:
        set_session_user(u)
        return u
    return cl.user_session.get("user")


# --------------------------- Notification Helpers ---------------------------

async def send_success(msg: str):
    await cl.Message(
        content=f"### ✅ Success\n\n{msg}",
        author="System"
    ).send()

async def send_info(msg: str):
    await cl.Message(
        content=f"### ℹ️ Information\n\n{msg}",
        author="System"
    ).send()

async def send_warning(msg: str):
    await cl.Message(
        content=f"### ⚠️ Warning\n\n{msg}",
        author="System"
    ).send()

async def send_error(msg: str):
    await cl.Message(
        content=f"### ❌ Error\n\n{msg}",
        author="System"
    ).send()


# --------------------------- Action Buttons ---------------------------

def get_auth_actions():
    """Actions for logged-out users"""
    return [
        cl.Action(name="login", label="🔑 Login", value="login"),
        cl.Action(name="signup", label="✨ Sign Up", value="signup"),
    ]

def get_user_actions():
    """Actions for logged-in users"""
    return [
        cl.Action(name="ask_examples", label="💡 Examples", value="ask_examples"),
        cl.Action(name="profile", label="👤 Profile", value="profile"),
        cl.Action(name="logout", label="🚪 Logout", value="logout"),
    ]


# --------------------------- Modal Forms ---------------------------

async def show_login_form():
    """Enhanced login form with better UX"""
    res = await cl.AskUserMessage(
        content="""# 🔑 Sign In to LegaBot

Enter your credentials to access your account.
Type Ok to enter credentials 

---
""",
        timeout=100,
        author="Authentication",
    ).send()
    
    # Collect email and password
    email_res = await cl.AskUserMessage(
        content="**Email Address:**",
        timeout=120,
        author="Login"
    ).send()
    
    if not email_res or not email_res.get("output"):
        return None
    
    password_res = await cl.AskUserMessage(
        content="**Password:**\n\n*Your password is hidden for security*",
        timeout=120,
        author="Login"
    ).send()
    
    if not password_res or not password_res.get("output"):
        return None
    
    return {
        "email": email_res.get("output", "").strip(),
        "password": password_res.get("output", "").strip()
    }


async def show_signup_form():
    """Enhanced signup form with validation"""
    await cl.Message(
        content="""# ✨ Create Your LegaBot Account

Join us to access powerful legal research tools.

---
""",
        author="Registration"
    ).send()
    
    # Full name
    name_res = await cl.AskUserMessage(
        content="**Full Name:**",
        timeout=120,
        author="Sign Up"
    ).send()
    
    if not name_res or not name_res.get("output"):
        return None
    
    # Email
    email_res = await cl.AskUserMessage(
        content="**Email Address:**",
        timeout=120,
        author="Sign Up"
    ).send()
    
    if not email_res or not email_res.get("output"):
        return None
    
    # Password
    pass_res = await cl.AskUserMessage(
        content="**Password:**\n\n*Minimum 6 characters*",
        timeout=120,
        author="Sign Up"
    ).send()
    
    if not pass_res or not pass_res.get("output"):
        return None
    
    # Confirm password
    confirm_res = await cl.AskUserMessage(
        content="**Confirm Password:**",
        timeout=120,
        author="Sign Up"
    ).send()
    
    if not confirm_res or not confirm_res.get("output"):
        return None
    
    return {
        "full_name": name_res.get("output", "").strip(),
        "email": email_res.get("output", "").strip(),
        "password": pass_res.get("output", "").strip(),
        "confirm": confirm_res.get("output", "").strip()
    }


# --------------------------- Entry Point ---------------------------

@cl.on_chat_start
async def on_start():
    """Initialize chat with appropriate welcome message"""
    user = get_session_user()
    
    if user:
        email = user.get('email', 'User')
        await cl.Message(
            content=f"{LOGGED_IN_MSG}\n\n**Logged in as:** {email}",
            actions=get_user_actions(),
        ).send()
    else:
        await cl.Message(
            content=WELCOME_MSG,
            actions=get_auth_actions(),
        ).send()


# --------------------------- Action Handlers ---------------------------

@cl.action_callback("login")
async def handle_login(action: cl.Action):
    """Handle login flow"""
    form_data = await show_login_form()
    
    if not form_data:
        await send_warning("Login cancelled.")
        return
    
    email = form_data.get("email", "")
    password = form_data.get("password", "")
    
    if not email or not password:
        await send_warning("Please provide both email and password.")
        return
    
    try:
        login_email_password(email, password)
        u = current_user()
        
        if u:
            set_session_user(u)
            await send_success(f"Welcome back! You're now logged in as **{u.get('email', '')}**")
            await cl.Message(
                content=LOGGED_IN_MSG,
                actions=get_user_actions(),
            ).send()
        else:
            await send_warning("Login succeeded but no active session found. Please try again.")
            
    except Exception as e:
        error_msg = str(e).lower()
        
        # Handle email confirmation error
        if "confirm" in error_msg or "not confirmed" in error_msg:
            if resend_confirmation:
                await send_warning(
                    "Your email address hasn't been verified yet.\n\n"
                    "Would you like us to resend the verification email?"
                )
                try:
                    resend_confirmation(email)
                    await send_success(
                        "Verification email sent! Please check your inbox (and spam folder)."
                    )
                except Exception as re:
                    await send_error(f"Failed to resend verification: {re}")
            else:
                await send_info(
                    "Please verify your email address using the link we sent you, then try logging in again."
                )
        else:
            await send_error(f"Login failed: {e}")


@cl.action_callback("signup")
async def handle_signup(action: cl.Action):
    """Handle signup flow"""
    form_data = await show_signup_form()
    
    if not form_data:
        await send_warning("Sign up cancelled.")
        return
    
    full_name = form_data.get("full_name", "")
    email = form_data.get("email", "")
    password = form_data.get("password", "")
    confirm = form_data.get("confirm", "")
    
    # Validation
    if not full_name:
        await send_warning("Please enter your full name.")
        return
    
    if not email or "@" not in email:
        await send_warning("Please enter a valid email address.")
        return
    
    if len(password) < 6:
        await send_warning("Password must be at least 6 characters long.")
        return
    
    if password != confirm:
        await send_warning("Passwords don't match. Please try again.")
        return
    
    # Attempt signup
    ok, msg = signup_email_password(email, password, full_name)
    
    if ok:
        await cl.Message(
            content="""# 🎉 Account Created Successfully!

Your LegaBot account has been created.

**Next steps:**
1. Check your email for a verification link
2. Click the link to verify your account
3. Come back and login

---

*You can now proceed to login!*
""",
            actions=[cl.Action(name="login", label="🔑 Login Now", value="login")],
        ).send()
    else:
        await send_error(f"Registration failed: {msg}")


@cl.action_callback("logout")
async def handle_logout(action: cl.Action):
    """Handle logout with confirmation"""
    confirm_msg = await cl.AskUserMessage(
        content="""# 🚪 Confirm Logout

Are you sure you want to logout from LegaBot?

Type **yes** to confirm or **no** to cancel.
""",
        timeout=60,
        author="Logout"
    ).send()
    
    if not confirm_msg:
        await send_info("Logout cancelled.")
        return
    
    response = confirm_msg.get("output", "").lower().strip()
    
    if response != "yes":
        await send_info("Logout cancelled.")
        return
    
    try:
        sb_logout()
    finally:
        set_session_user(None)
        await cl.Message(
            content="""# 👋 Logged Out Successfully

You have been logged out from LegaBot.

You can login again or create a new account anytime.
""",
            actions=get_auth_actions(),
        ).send()


@cl.action_callback("profile")
async def handle_profile(action: cl.Action):
    """Display user profile"""
    user = get_session_user()
    
    if not user:
        await send_warning("You need to be logged in to view your profile.")
        await cl.Message(
            content=WELCOME_MSG,
            actions=get_auth_actions(),
        ).send()
        return
    
    email = user.get("email", "Not available")
    name = user.get("full_name", "Not available")
    user_id = user.get("id", "Not available")
    
    profile_info = f"""# 👤 Your Profile

**Name:** {name}

**Email:** {email}

**User ID:** {user_id}

---

*Need to update your information? Contact support.*
"""
    
    await cl.Message(
        content=profile_info,
        actions=get_user_actions(),
    ).send()


@cl.action_callback("ask_examples")
async def handle_examples(action: cl.Action):
    """Show example questions"""
    await cl.Message(
        content=EXAMPLES_MSG,
        actions=[
            cl.Action(name="example_query", label="What is theft under IPC?", 
                     value="What constitutes theft under IPC Section 378?"),
            cl.Action(name="example_query", label="Punishment for murder", 
                     value="Explain the punishment for murder under IPC"),
            cl.Action(name="example_query", label="Bail provisions", 
                     value="What are the bail provisions in CrPC?"),
            cl.Action(name="example_query", label="Fundamental rights", 
                     value="What are fundamental rights under the Constitution?"),
        ],
    ).send()


@cl.action_callback("example_query")
async def handle_example_query(action: cl.Action):
    """Handle example question selection"""
    await process_legal_query(action.value)


# --------------------------- Message Handler ---------------------------

@cl.on_message
async def handle_message(message: cl.Message):
    """Main message handler"""
    user = get_session_user()
    
    if not user:
        await cl.Message(
            content="""# 🔐 Authentication Required

You need to be logged in to use LegaBot.

Please login or create an account to continue.
""",
            actions=get_auth_actions(),
        ).send()
        return
    
    query = message.content.strip()
    await process_legal_query(query)


async def process_legal_query(query: str):
    """Process and respond to legal queries"""
    if not query:
        await send_warning("Please enter a valid question.")
        return
    
    # Show processing message
    processing_msg = await cl.Message(
        content=f"""# 🔍 Processing Your Query

**Question:** {query}

*Searching through legal documents and generating answer...*

⏳ This may take a few moments.
"""
    ).send()
    
    try:
        # Get answer from RAG pipeline
        answer = get_legal_answer(query)
        
        # Format and send response
        formatted_answer = f"""# ⚖️ Legal Research Result

**Your Question:**
> {query}

---

## Answer

{answer}

---

*💡 Have another question? Just type it below!*
"""
        
        await cl.Message(
            content=formatted_answer,
            actions=get_user_actions()
        ).send()
        
    except Exception as e:
        await send_error(
            f"An error occurred while processing your query:\n\n`{str(e)}`\n\n"
            "Please try again or rephrase your question."
        )