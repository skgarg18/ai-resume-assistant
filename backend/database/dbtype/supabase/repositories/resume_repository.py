class ResumeRepository:

    def __init__(self , db):
        self.db = db

    def add_resume_data(self, resume_data: dict):
        # Add resume data to the database
        try:
            response = self.db.table("resumes")\
                .insert(resume_data)\
                .execute()
            
            return response
        
        except Exception as e:
            print(f"Error adding resume data: {e}\n")
            return None  
        
    
    def delete_resume_data_by_session(self, session_id: str):
        # Delete resume data by session_id
        try:

            response = self.db.table("resumes")\
                .delete()\
                .eq("session_id", session_id)\
                .execute()
            
            return response

        except Exception as e:

            print(f"Error deleting resume data: {e}\n")    
            return None




    def get_resume_data_ordered_by_score(self , session_id):
        
        try:

            results = (
                self.db
                .table("resumes")
                .select("*")
                .eq("session_id", session_id)
                .order("score", desc=True)
                .execute()
            )

            return results.data
        
        except Exception as e:
            print(f"Eroor fetching resume data : {e}")
            return None
        
    

    def get_candidate_email(
        self,
        session_id: str,
        candidate_name: str
    ) -> str | None:
        
        """
        This functions extracts candidate email from canditate name
        """

        response = (
            self.db.table("resumes")
            .select("email")
            .eq("session_id", session_id)
            .ilike("name", candidate_name)
            .execute()
        )

        if response.data:
            return [row["email"] for row in response.data]

        return None
        

    

