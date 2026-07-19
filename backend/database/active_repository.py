"""
This file stores imports from all db types repositories
We simply have to comment out the import of db type that we want to work with
"""

# ------------------------------------------------------------
# Supabase
# -------------------------------------------------------------
# from database.dbtype.supabase.combined_repository import *


# ---------------------------------------------------------------
# Local Storage
# ----------------------------------------------------------------
from  database.dbtype.local_storage.combined_repository import *
from database.dbtype.local_storage.postgres.init_db import init_db

init_db()