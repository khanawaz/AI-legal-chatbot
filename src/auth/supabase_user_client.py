# src/auth/supabase_user_client.py
from __future__ import annotations
import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_KEY")

def make_user_client(access_token: str) -> Client:
    """
    Build a Supabase client authenticated AS THE USER (with their JWT).
    Required for Postgres RLS policies to allow per-user reads/writes.
    """
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        raise RuntimeError("Missing SUPABASE_URL / SUPABASE_ANON_KEY in environment.")
    c = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    # Attach user JWT so PostgREST sees auth.uid()
    c.postgrest.auth(access_token)
    return c
