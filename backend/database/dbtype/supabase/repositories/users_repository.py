class UserRepository:

    def __init__(self , db):
        self.db = db

    
    def update_or_insert_user_data(self , google_id , email , name , picture , refresh_token):

        try:
            response = self.db.table("users").upsert(
                {
                    "google_id": google_id,
                    "email": email,
                    "name": name,
                    "picture": picture,
                    "refresh_token": refresh_token,
                },
                on_conflict="google_id",
            ).execute()

            return response
        
        except Exception as e:
            print(f"Error Upserting user data for {email} : {e}\n")
            return None

    

    def get_refresh_token_by_id(self , user_id):

        try:
            result = (
                self.db.table("users")
                .select("refresh_token")
                .eq("user_id", user_id)
                .single()
                .execute()
            )

            return result

        except Exception as e:
            print(f"Error fetching refresh token: {e}\n")
            return None
        
    

    def get_user_data_by_google_id(self , google_id):

        try:
            result = (
                self.db.table("users")
                .select("user_id")
                .eq("google_id", google_id)
                .single()
                .execute()
            )

            return result.data
        
        except Exception as e:
            print(f"Error fetching user data for google_id {google_id} : {e}\n")
            return None
