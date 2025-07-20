from app.db.setup import get_db
from app.services.erp_extractor import ERPTaskExtractor
from app.config.settings import ERP_PASSWORD


def _get_db_session():
    return get_db()


def get_user_data(email: str):
    print(f"Fetching password for {email} from database...")

    # Yet to integrate the DB based fetching

    if email.lower() == "pugazhendhi.kumar@softsuave.org":
        return ERP_PASSWORD


def get_tasks(user_email: str, user_password: str):
    print(f"Fetching ERP tasks for (Email: {user_email}, Password: {user_password})...")
    erp_extractor = ERPTaskExtractor(user_email, user_password)
    fetched_tasks = erp_extractor.run()
    return fetched_tasks

