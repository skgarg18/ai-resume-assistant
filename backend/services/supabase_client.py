# supabase_client.py

import os
from dotenv import load_dotenv
from supabase import create_client,Client

load_dotenv()

# Creating supabase client
supabase: Client = create_client(
   os.environ.get("SUPABASE_URL"),
   os.environ.get("SUPABASE_KEY")
)

# Bucket name of storing resume pdfs
bucket_name = "resume-files"

