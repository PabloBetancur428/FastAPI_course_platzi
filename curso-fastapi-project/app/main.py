from fastapi import FastAPI, Request
from datetime import datetime, time
import zoneinfo
from db import create_all_tables
from sqlmodel import select
from .routers import customers, transactions, invoices, plans


app = FastAPI(lifespan=create_all_tables) # to run a thing in the beginning and at the end
app.include_router(customers.router)
app.include_router(transactions.router)
app.include_router(invoices.router)
app.include_router(plans.router)
#Para decir que este método es un endopoint, se usa el decorador app.get


# @app.middleware("http")
# async def log_request_time(request: Request):
#     start_time = time.time()
#     response = await call_next(request)
#     process_time = time.time() - start_time
#     print(f"Request: {request.url} completed in: {process_time:.4f} seconds")

#     return response

@app.get("/") #slash es el root, sale inmediato
async def root():
    return {"message": "Hello Luis!"}

country_timezones = {
    "CO": "America/Bogota",
    "MX": "America/Mexico_City",
    "AR": "America/Argentina/Buenos_Aires",
    "BR": "America/Sao_Paulo",
    "PE": "America/Lima"
}


@app.get("/time/{iso_code}") #{} es para recibir variables
async def get_time(iso_code: str):
    #Get current time in ISO 8601 format
    iso = iso_code.upper()
    timezone_str = country_timezones.get(iso)
    tz = zoneinfo.ZoneInfo(timezone_str)
    current_time = datetime.now(tz)
    return {"current_time": current_time}





