from typing import Optional

from fastapi import FastAPI, Form, Header, HTTPException, status, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


import hashlib
import secrets
import random
import datetime

# import os
# import redis


# users = redis.Redis(
#     host="localhost",
#     port="8000",
#     db=0)

# session = redis.Redis()

app = FastAPI()

# dummy = passwordkuat123
# delta = delta123
# alpha = alpha0101

users = {
    "1111" : {
        "dummy" : {
            "username" : "dummy",
            "full_name" : "Dummy McGregor",
            "npm" : "1906350862",
            "hashed_password" : "b0d1f35fada855049a2a014138fddfb55ced7b85",
            "client_id" : "1111",
            "client_secret" : "2222",
            "token" : "",
            "token_expire" : "",
            "refresh_token" : ""
        },
        "delta" : {
            "username": "delta",
            "full_name": "Delta Gittens",
            "npm": "1906354212",
            "hashed_password": "b00f66d87bb00ca2ccb207bfa3de4110b0da88b9",
            "client_id": "1111",
            "client_secret": "2660",
            "token": "",
            "token_expire" : "",
            "refresh_token": ""
        }
    },
    "2222" : {
        "alpha" : {
            "username": "alpha",
            "full_name": "Alpha Tankian",
            "npm": "1906344158",
            "hashed_password": "b2a259f0eeb3cead3093fa2a3915d2b49603e1d5",
            "client_id": "2222",
            "client_secret": "3527",
            "token": "",
            "token_expire" : "",
            "refresh_token": ""
        }
    }
}

tokens = {}

def hash_password(password: str):
    #using SHA1
    hash_object = hashlib.sha1(password.encode())
    hex_dig = hash_object.hexdigest()
    return hex_dig

def user_is_valid(username: str, password: str, client_id: str, client_secret: str):
    current_user = users[client_id][username]

    stored_password = current_user["hashed_password"]
    input_password = hash_password(password)

    stored_client_secret = current_user["client_secret"]
    input_client_secret = client_secret

    return ((stored_password == input_password) and (stored_client_secret == input_client_secret))

def generate_token():
    #Generating 20 bytes / 40 char length string
    token = secrets.token_hex(20)
    return token

def generate_clientid():
    clientid = random.randint(1000, 9999)
    if clientid_exist(clientid):
        clientid = generate_clientid()
    else:
        return clientid

def generate_clientpassword():
    clientpassword = random.randint(1000, 9999)
    return clientpassword

def error_message(error, error_description):
    return {
        "error" : error,
        "error_description" : error_description
    }


# @app.post("/oauth/register")
# def register(
#     username: str = Form(...),
#     password: str = Form(...),
#     fullname: str = Form(...),
#     npm: str = Form(...),
#     ):

    # client_id = generate_clientid()

#     if username in users[client_id]:
#         return {
#             "status" : "Failed",
#             "description" : "Username has been used!"
#         }



#     users.hmset("username", {
#         "username" : username,
#         "full_name" : fullname,
#         "npm" : npm,
#         "hashed_password" : hash_password(password),
#         "client_id" : generate_clientid(),
#         "client_secret" : generate_clientpassword(),
#     } )

#     return {
#         "status" : "registered",
#         "user" : users.get(username)
#     }

# @app.get("/oauth/getuser")
# def read_root(username: str):
#     return {username: users[username]}


@app.post("/oauth/token")
def token(
    username: str = Form(...), 
    password: str = Form(...), 
    grant_type: str = Form(None, regex="password"), 
    client_id: str = Form(...), 
    client_secret: str = Form(...)
    ):
    try: 
        if user_is_valid(username, password, client_id, client_secret):

            current_user = users[client_id][username]

            access_token = generate_token()
            refresh_token = generate_token()

            current_user["token"] = access_token
            current_user["refresh_token"] = refresh_token
            current_user["token_expire"] = datetime.datetime.now() + datetime.timedelta(minutes=5)

            tokens[access_token] = {"client_id" : client_id, "username" : username}

            return {
                "access_token" : access_token,
                "expires_in" : 300,
                "token_type" : "Bearer",
                "scope" : None,
                "refresh_token" : current_user["refresh_token"]
            }

        raise

    except:
        return JSONResponse(
        status_code = 401,
        content = error_message("invalid_request", "Ada yang salah masbro")
    )

@app.post("/oauth/resource")
async def resource(Authorization: Optional[str] = Header(None)):
    try:
        auth_split = Authorization.split()
        if auth_split[0] != "Bearer":
            raise
        token = auth_split[1]

        current_user_identification = tokens[token]
        current_user = users[current_user_identification["client_id"]][current_user_identification["username"]]

        if current_user["token_expire"] > datetime.datetime.now():
            return {
                "access_token" : token,
                "client_id" : current_user["client_id"],
                "user_id" : current_user["username"],
                "full_name" : current_user["full_name"],
                "npm" : current_user["npm"],
                "expires" : None,
                "refresh_token" : current_user["refresh_token"]
            }
        else:
            del tokens[token]
            raise
    except:
        return JSONResponse(
            status_code = 401,
            content = error_message("invalid_token", "Token salah masbro")
        )