class ResumeChunksRepository:

    def __init__(self , db):
        self.db = db
    

    def add_resume_chunks(self, chunk_data: dict):

        # Add resume chunks to the database
        try:
            response = self.db.table("resume_chunks")\
                .insert(chunk_data)\
                .execute()
            
            return response
        
        except Exception as e:
            print(f"Error adding resume chunk data: {e}")
            return None
    

    def delete_resume_chunks_by_session(self, session_id: str):
        # Delete resume chunks by session_id
        try:
            response = self.db.table("resume_chunks")\
            .delete()\
            .eq("session_id", session_id)\
            .execute()

            return response
        
        except Exception as e:
            print(f"Error deleting resume chunks: {e}")
            return None
    



    def derive_top_resume_chunks_similarity_search(
        self ,
        session_id , 
        candidate_name , 
        query_embedding , 
        match_count
    ):

        try:
            results = self.db.rpc(
                "match_resume_chunks",
                {
                    "p_session_id": session_id,
                    "p_candidate_name": candidate_name,
                    "query_embedding": query_embedding,
                    "match_count": match_count
                }
            ).execute()

            return results.data
        
        except Exception as e:
            print(f"Error deriving top resume chunks similarity search: {e}\n")
            return None


        