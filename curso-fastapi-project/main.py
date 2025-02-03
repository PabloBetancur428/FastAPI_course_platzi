from fastapi import FastAPI
from datetime import datetime

app = FastAPI()

#Para decir que este método es un endopoint, se usa el decorador app.get
@app.get("/") #slash es el root, sale inmediato
async def root():
    return {"message": "Hello Luis!"}

@app.get("/time")
async def get_time():
    #Get current time in ISO 8601 format
    current_time = datetime.now().isoformat()
    return {"current_time": current_time}
