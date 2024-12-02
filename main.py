import json
import uvicorn

from typing import Union
from fastapi import FastAPI, HTTPException, Response, Request
from models.ActivativationValidate import ActivationValidate
from utils.database import execute, fetch_query_as_json
from utils.security import validate, validate_before_activation, validate_func

from fastapi.middleware.cors import CORSMiddleware
from models.UserRegister import UserRegister 
from models.UserLogin import UserLogin
from models.EmailActivation import EmailActivation

from datetime import datetime, timezone
import os
from dotenv import load_dotenv

from utils.time import convert_minutes_to_time

load_dotenv()

timezone_name = os.getenv("TIMEZONE", "UTC")
print(f"Aplicación iniciada en el huso horario: {timezone_name}")

utc_time = datetime.now(timezone.utc)
print(f"Hora en UTC: {utc_time}")


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
        return { "data": result_dict, "version": "0.0.12" }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/register")
async def register(user: UserRegister):
    return  await register_user_firebase(user)

# Me va a devolver el token y el estado del usuario (activo o inactivo)
@app.post("/login")
async def login_custom(user: UserLogin):
    return await login_user_firebase(user)

@app.get("/user")
@validate
async def user(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-cache";

    email = request.state.email

    # Consulto cuado activo la cuenta
    query = f"""
        SELECT DATEDIFF(MINUTE, actived_at, GETDATE()) AS timeTrans
        FROM proyecto_expertos.users
        WHERE email = '{email}';"""
    
    try:
        result = await fetch_query_as_json(query)
        result_dict = json.loads(result)

        minutes_trans = result_dict[0].get('timeTrans')

        # Conversion
        years, months, days, hours = convert_minutes_to_time(minutes_trans)

        return {
            "email": email
            , "firstname": request.state.firstname
            , "lastname": request.state.lastname
            , "timeTrans": {
                "y": years,
                "months": months,
                "days": days,
                "hours": hours,
                "minutes": minutes_trans
            }
        }

    except Exception as e:
        print(f"Error validando el código: {e}")
        raise HTTPException(status_code=500, detail="Error al calcular tiempo transcurrido desde la activacion de la cuenta.")


# API que va a consumir la function app - para validar el usuario
@app.post("/user/{email}/code")
@validate_func  # wrapper o decorador
async def generate_code(request: Request, email: str):
    e = EmailActivation(email=email)
    return await generate_activation_code(e)

@app.post("/activation")
@validate_before_activation
async def user_activation(request: Request, response: Response, code: ActivationValidate):
    response.headers["Cache-Control"] = "no-cache"

    # Email ya validado por el decorador
    email = request.state.email

    # Paso 1: Validar que el código sea válido
    validate_query = f"""
        EXEC proyecto_expertos.validate_code @Email = '{email}', @Code = {code.code}
    """
    try:
        result = await fetch_query_as_json(validate_query, True)
        result_dict = json.loads(result)

        print(result_dict)

        # Si el código no es válido, devolver error
        if not result_dict or not result_dict[0].get("IsValid"):
            raise HTTPException(status_code=400, detail="El código es inválido o ha expirado.")

    except Exception as e:
        print(f"Error validando el código: {e}")
        raise HTTPException(status_code=500, detail="Error validando el código.")

    # Paso 2: Activar al usuario
    activate_query = f"""
        UPDATE proyecto_expertos.users 
        SET active = 1, actived_at = GETDATE()
        WHERE email = '{email}';
    """
    try:
        await execute(activate_query)
        return {"message": "Usuario activado correctamente."}

    except Exception as e:
        print(f"Error activando el usuario: {e}")
        raise HTTPException(status_code=500, detail="Error al activar el usuario.")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)