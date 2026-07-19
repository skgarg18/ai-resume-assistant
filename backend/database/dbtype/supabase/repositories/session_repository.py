"""
This file handles table operations of sessions table
"""

class SessionRepository:

    def __init__(self , db):
        self.db = db


    def add_session_details(self, session_id: str, session_name: str, jd_description: str):
        # Add a new session to the database

        try:
            response = self.db.table("sessions").insert({
                "session_id": session_id,
                "session_name": session_name,
                "job_description": jd_description
            }).execute()

            return response
        
        except Exception as e:
            print(f"Error adding session details: {e}\n")
            return None
    



    def delete_session_by_id(self, session_id: str):    
        # Delete session by session_id
        try:
            response = self.db.table("sessions")\
                .delete()\
                .eq("session_id", session_id)\
                .execute()
            
            return response

        except Exception as e:
            print(f"Error deleting session: {e}\n")
            return None
    

    def get_sessions(self):

        try:
            response = (
                self.db.table("sessions")
                .select("session_id, session_name, created_at")
                .order("created_at", desc=True)
                .execute()
            )

            return response.data
        
        except Exception as e:
            print(f"Error fetching session: {e}")
            return None
