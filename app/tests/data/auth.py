from app.environment import settings

USER = { 
    "name": "John", 
    "surname": "Smith", 
    "email": "johnsmith@gmail.com", 
    "password": "johnsmith" 
}

USER_LOGIN = {
    "email": "johnsmith@gmail.com",
    "password": "johnsmith"
}

USER_WRONG_PASS_LOGIN = {
    "email": "johnsmith@gmail.com",
    "password": "wrongpassword"
}

SAME_EMAIL_USER = {
    "name": "Alex",
    "surname": "Jones",
    "email": "johnsmith@gmail.com",
    "password": "alexjones"
}

TRUE_ADMIN = { 
    "name": "Admin", 
    "surname": "Admin", 
    "email": "adminadmin@gmail.com", 
    "password": "adminadmin",
    "admin_password": settings.ADMIN_PASSWORD
}

TRUE_ADMIN_LOGIN = {
    "email": "adminadmin@gmail.com",
    "password": "adminadmin"
}

FAKE_ADMIN = { 
    "name": "Henry", 
    "surname": "James", 
    "email": "henryjames@gmail.com", 
    "password": "henryjames",
    "admin_password": "wrongpassword"
}

EMAIL = { "email": "johnsmith@gmail.com" }