
class ChatHistoryRepository:


    def __init__(self , db):
        self.db = db
    

    def add_chat_history(self , 
                         session_id:str ,
                         message_type:str , 
                         user_message: str , 
                         assistant_message: str|None = None ,
                         email_id : str|None = None , 
                         email_subject : str|None = None , 
                         email_body : str|None = None , 
                         draft_id : int|None = None ,
                         email_meeting_metadata: dict|None = None ):

        try:
            self.db.table("chat_history").insert({
                "session_id" : session_id,
                "message_type": message_type,
                "user_message" : user_message,
                "assistant_message" : assistant_message,
                "email_id": email_id,
                "email_subject": email_subject,
                "email_body": email_body,
                "draft_id" : draft_id,
                "email_meeting_metadata" : email_meeting_metadata,
            }).execute()

            return True
        

        except Exception as e:
            print(f"Error adding chat history: {e}\n")
            return False
    




    def get_chat_history_by_session_id(self , session_id):

        try:
            response = (
                self.db.table("chat_history")
                .select("*")
                .eq("session_id", session_id)
                .order("created_at")
                .execute()
            )

            return response.data
    
        except Exception as e:
            print(f"Error in feting chat History for session : {session_id} , : {e}\n")
            return None