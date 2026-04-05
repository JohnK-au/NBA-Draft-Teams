"""
Supabase client singleton.

HOW TO SET UP:
1. Go to supabase.com → your project → Settings → API
2. Copy "Project URL" and "service_role" key (NOT the anon key — service_role
   bypasses row-level security, which is what you want for a backend server)
3. Add these to your environment:
     SUPABASE_URL=https://xxxx.supabase.co
     SUPABASE_SERVICE_KEY=eyJ...
   On Render: Dashboard → your service → Environment → Add env var
   Locally: add to a .env file (and add .env to .gitignore if not already)

WHY A SINGLETON?
Creating a Supabase client is cheap, but there's no reason to recreate it on
every request. This module creates it once at import time and reuses it.
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Loads variables from .env into os.environ when running locally.
# In production (Render), env vars are set in the dashboard and this is a no-op.
load_dotenv()


def get_client() -> Client:
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_SERVICE_KEY")

    if not url:
        raise RuntimeError("Missing environment variable: SUPABASE_URL")
    if not key:
        raise RuntimeError("Missing environment variable: SUPABASE_SERVICE_KEY")

    return create_client(url, key)


# Module-level singleton — created once at import time and reused across requests.
# Other modules import this: `from backend.services.supabase_client import db`
db: Client = get_client()
