def extract_details(user_info):

    data = {}

    name = (user_info.get("name") or "").replace(".", " ")
    name = " ".join(name.split())  # Remove extra spaces

    data["name"] = name.title()
    data["email"] = user_info.get("email") or ""
    data["phone"] = user_info.get("phone") or ""

    return data