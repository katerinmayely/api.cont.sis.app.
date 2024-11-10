import json

from typing import Union

from fastapi import FastAPI, HTTPException
from utils.database import fetch_query_as_json

app = FastAPI()

@app.get("/")
async def read_root():
    query = "SELECT * FROM proyecto_expertos.prueba"
    try:
        result = await fetch_query_as_json(query)
        result_dict = json.loads(result)
        return { "data": result_dict, "version": "0.0.3" }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/items/{item_id}")
def read_item(item_id: int, q: Union[str, None] = None):
    return {"item_id": item_id, "q": q}