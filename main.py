import json
import uvicorn

from typing import Union
from fastapi import FastAPI, HTTPException, Response, Request
from utils.database import fetch_query_as_json
from utils.security import validate, validate_func

from fastapi.middleware.cors import CORSMiddleware
from models.UserRegister import UserRegister 
from models.UserLogin import UserLogin
from models.EmailActivation import EmailActivation

from controllers.firebase import register_user_firebase, login_user_firebase, generate_activation_code

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],  # Permitir todos los encabezados
)


@app.get("/")
async def read_root():
    query = "SELECT * FROM proyecto_expertos.prueba"
    try:
        result = await fetch_query_as_json(query)
        result_dict = json.loads(result)
        return { "data": result_dict, "version": "0.0.11" }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/register")
async def register(user: UserRegister):
    return  await register_user_firebase(user)

@app.post("/login")
async def login_custom(user: UserLogin):
    return await login_user_firebase(user)

@app.get("/user")
@validate
async def user(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-cache";
    return {
        "email": request.state.email
        , "firstname": request.state.firstname
        , "lastname": request.state.lastname
    }

@app.get("/validation/{code}")
async def user(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-cache";
    return {
        "email": request.state.email
        , "firstname": request.state.firstname
        , "lastname": request.state.lastname
    }

# API que va a consumir la function app - para validar el usuario
@app.post("/user/{email}/code")
@validate_func  # wrapper o decorador
async def generate_code(request: Request, email: str):
    e = EmailActivation(email=email)
    return await generate_activation_code(e)

    
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)