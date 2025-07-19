from app.db.setup import get_db
from app.services.erp_extractor import ERPTaskExtractor

def _get_db_session():
    return get_db()


def get_user_data(name: str):
    if not name.lower() in "pugazhendhi kumar":
        return {"Error": "User not exist"}

    # Use the generator properly
    for db in get_db():
        user = db.users.find_one({"full_name": name})
        if user:
            return {"email": user["email"], "password": "#PK@2002.in"}
        else:
            return {"Error": "User not found in database"}


def get_tasks(user_email: str, user_password: str):
    erp_extractor = ERPTaskExtractor(user_email, user_password)
    fetched_tasks = erp_extractor.run()
    return fetched_tasks

print(get_tasks(user_email="pugazhendhi.kumar@softsuave.org", user_password="#PK@2002.in"))

# print(get_user_data("Pugazhendhi Kumar"))

