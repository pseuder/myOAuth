from db_module import db_operation, exec_sql
from log_module import setup_logger

global LOGGER
LOGGER = setup_logger("business", "logs/business")


@db_operation
def get_user(cursor, args):
    if "username" not in args:
        return {"status": "warning", "data": "", "message": "username is required"}
    
    sql = "SELECT * FROM users WHERE username = %s"
    exec_sql(cursor, sql, (args["username"],))
    queryResult = cursor.fetchall()
    return {"status": "success", "data": queryResult, "message": ""}

@db_operation
def add_user(cursor, user_info):
    if "username" not in user_info or "email" not in user_info or "sub" not in user_info:
        return {"status": "warning", "data": "", "message": "username, email, sub are required"}
    
    sql = "INSERT INTO users (username, email, sub) VALUES (%s, %s, %s)"
    exec_sql(cursor, sql, (user_info["username"], user_info["email"], user_info["sub"]))
    return {"status": "success", "data": cursor.lastrowid, "message": "加入成功"}