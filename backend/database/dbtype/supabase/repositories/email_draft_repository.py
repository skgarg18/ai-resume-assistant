

class EmailDraftRepository:

    def __init__(self , db):
        self.db = db


    def add_data_email_draft(
            self , 
            session_id ,
            candidate_name , 
            candidate_email , 
            subject , 
            body , 
            status , 
            original_prompt , 
            meeting_metadata ):

        try:

            response = self.db.table("email_drafts").insert({
                "session_id": session_id,
                "candidate_name": candidate_name,
                "recipient_email": candidate_email,
                "subject": subject,
                "body": body,
                "status": status,
                "original_prompt": original_prompt,
                "meeting_metadata": meeting_metadata,
            }).execute()

            return response.data

        except Exception as e:
            print(f"Error uploading email drafts data: {e}\n")
            return None
    




    def get_data_by_draft_id(self , draft_id):

        try:

            result = (
                self.db.table("email_drafts")
                .select("*")
                .eq("id", draft_id)
                .single()
                .execute()
            )

            return result.data
        
        except Exception as e:
            print(f"Error uploading email drafts data: {e}\n")
            return None
        

    

    def update_regenerate_email_draft_by_id(self , draft_id , subject , body , regeneration_count ,updated_at ,  meeting_metadata):

        
        try:

            result = (
                self.db.table("email_drafts")
                .update({
                    "subject": subject,
                    "body": body,
                    "regeneration_count": regeneration_count,
                    "updated_at": updated_at,
                    "meeting_metadata": meeting_metadata
                })
                .eq("id", draft_id)
                .execute()
            )

            return result
        
        except Exception as e:
            print(f"Error updating regenerate email drafts data: {e}\n")
            return None
    


    def update_sent_email_draft(self , draft_id,  sent_at , updated_at , meeting_metadata):

        try : 
            response = self.db.table("email_drafts")\
                .update({
                    "status": "sent",
                    "sent_at": sent_at,
                    "updated_at": updated_at,
                    "meeting_metadata": meeting_metadata
                })\
                .eq("id", draft_id)\
                .execute()
            
            return response

        except Exception as e:
            print(f"Error in Updating email Sent Status : {e}")
            return None
        

