import requests

SERVER_URL = "http://127.0.0.1:5000"

def login(current_session, username, password):
    print("### LOG IN ###")
    payload = {
        "username": username,
        "password": password
    }
    response = current_session.post(
        f"{SERVER_URL}/api/login",
        json=payload
    )
    print("Status Code:", response.status_code)
    print("Response:", response.text)
    return response

def logout(current_session):
    print("### LOG OUT ###")
    response = current_session.post(f"{SERVER_URL}/api/logout")
    print("Status Code:", response.status_code)
    print("Response:", response.text)
    return response

def update_profile(current_session, first_name, last_name, student_id):
    print("### UPDATE PROFILE ###")
    payload = {
        "first_name": first_name,
        "last_name": last_name,
        "student_id": student_id
    }
    response = current_session.post(
        f"{SERVER_URL}/api/profile",
        json=payload
    )
    print("Status Code:", response.status_code)
    print("Response:", response.text)
    return response

def delete_profile(current_session):
    print("### DELETE PROFILE ###")
    response = current_session.delete(f"{SERVER_URL}/api/profile")
    print("Status Code:", response.status_code)
    print("Response:", response.text)
    return response

def get_profile(current_session):
    print("### GET PROFILE ###")
    response = current_session.get(f"{SERVER_URL}/api/profile")
    print("Status Code:", response.status_code)
    print("Response:", response.text)
    return response

def create_user(current_session, username,password):
    print("### CREATE USER ###")
    payload = {
        "username": username,
        "password": password,
    }
    response = current_session.post(
        f"{SERVER_URL}/api/user",
        json=payload
    )
    print("Status Code:", response.status_code)
    print("Response:", response.text)
    return response

def get_user(current_session):
    print("### GET USER ###")
    response = current_session.get(f"{SERVER_URL}/api/user")
    print("Status Code:", response.status_code)
    print("Response:", response.text)
    return response

def delete_user(current_session):
    print("### DELETE USER ###")
    response = current_session.delete(f"{SERVER_URL}/api/user")
    print("Status Code:", response.status_code)
    print("Response:", response.text)
    return response


if __name__ == "__main__":
    session = requests.Session()
    get_user(session)
    delete_user(session)
    get_profile(session)
    update_profile(session, "bryce", "reid", 1298718)
    login(session, "bryce_r", "1112")
    login(session, "bryce_r", "1111")
    get_user(session)
    update_profile(session, "ada", "lovelace", 1230)
    get_profile(session)
    delete_profile(session)
    update_profile(session, "bryce", "reid", 1298718)
    get_profile(session)
    create_user(session, "fred", "1234")
    logout(session)
    create_user(session, "fred", "1234")
    delete_profile(session)
    delete_user(session)
    login(session, "fred", "1234")


