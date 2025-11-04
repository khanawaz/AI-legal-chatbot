import os
from pathlib import Path
from dotenv import load_dotenv

try:
    from supabase import create_client, Client
except Exception:
    create_client, Client = None, object

PROJECT_ROOT = Path(__file__).resolve().parents[2]
load_dotenv(PROJECT_ROOT / ".env")

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")

_sb = None

def supabase() -> "Client":
    global _sb
    if _sb is not None:
        return _sb
    if not (SUPABASE_URL and SUPABASE_ANON_KEY):
        raise RuntimeError("Supabase not configured: set SUPABASE_URL and SUPABASE_ANON_KEY in .env")
    if create_client is None:
        raise RuntimeError("supabase-py not installed. Add `supabase>=2.4.0`.")
    _sb = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    return _sb
