from fastapi import FastAPI, HTTPException, status
from datetime import datetime
import zoneinfo
from models import Customer, CustomerCreate, Transaction, Invoice
from db import SessionDep, create_all_tables
from sqlmodel import select


app = FastAPI(lifespan=create_all_tables) # to run a thing in the beginning and at the end

#Para decir que este método es un endopoint, se usa el decorador app.get
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

db_customers : list[Customer] = []

#Con post se coge data
@app.post('/customers', response_model=Customer) #response para mostrar a fastapi que el tipo de data retornado es customer
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
    customer = Customer.model_validate(customer_data.model_dump()) #To retrieve a dict with data from user
    session.add(customer)
    session.commit()
    session.refresh(customer)

    return customer

@app.get("/customers/{customer_id}", response_model = Customer)
async def read_customer(customer_id: int, session: SessionDep):
    customer_db = session.get(Customer, customer_id) #query a base de datos

    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer does not exist")
    return customer_db

@app.delete("/customers/{customer_id}")
async def delete_customer(customer_id: int, session: SessionDep):
    customer_db = session.get(Customer, customer_id) #query a base de datos

    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer does not exist")
    
    session.delete(customer_db)
    session.commit() #confirms the query
    
    return {"detail": "ok"}


@app.get("/customers", response_model = list[Customer])
async def list_customer(session: SessionDep):
    return session.exec(select(Customer)).all()
    


@app.get("/customers/{customer_id}", response_model = Customer)
async def get_customer(customer_id: int):
    for customer in db_customers:
        if customer.id == customer_id:
            return customer
        
    raise HTTPException(status_code=404, detail = "Customer not found")



#Con post se coge data
@app.post('/transactions')
async def create_transaction(transaction_data: Transaction):
    return transaction_data

#Con post se coge data
@app.post('/invoices')
async def create_invoices(invoices_data: Invoice):
    return invoices_data
