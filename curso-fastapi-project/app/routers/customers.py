from fastapi import APIRouter, Query
from models import Customer, CustomerCreate, CustomerPlan, Plan, StatusEnum
from db import SessionDep
from fastapi import FastAPI, HTTPException, status
from models import Customer, CustomerCreate, CustomerUpdate, Transaction, Invoice
from sqlmodel import select


router = APIRouter()


@router.post('/customers', 
             response_model=Customer, 
             status_code = status.HTTP_201_CREATED,
             tags=['customers']) #response para mostrar a fastapi que el tipo de data retornado es customer
async def create_customer(customer_data: CustomerCreate, session: SessionDep):
    customer = Customer.model_validate(customer_data.model_dump()) #To retrieve a dict with data from user
    session.add(customer)
    session.commit()
    session.refresh(customer)

    return customer

@router.get("/customers/{customer_id}", response_model = Customer, tags=['customers'])
async def read_customer(customer_id: int, session: SessionDep):
    customer_db = session.get(Customer, customer_id) #query a base de datos

    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer does not exist")
    return customer_db


@router.patch("/customers/{customer_id}", 
           response_model = Customer, 
           status_code=status.HTTP_201_CREATED, tags=['customers']) #Hacer actualizaciones
async def update_customer(
    customer_id: int, customer_data: CustomerUpdate, session: SessionDep):

    customer_db = session.get(Customer, customer_id) #query a base de datos reales

    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer does not exist")
    
    customer_data_dict = customer_data.model_dump(exclude_unset=True) #toma todso los datos del usuario en body y lo vuelve dict
    customer_db.sqlmodel_update(customer_data_dict)
    session.add(customer_db) #agrega valores pasados
    session.commit()# los mete en la db
    session.refresh(customer_db)
    return customer_db



@router.delete("/customers/{customer_id}", tags=['customers'])
async def delete_customer(customer_id: int, session: SessionDep):
    customer_db = session.get(Customer, customer_id) #query a base de datos

    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Customer does not exist")
    
    session.delete(customer_db)
    session.commit() #confirms the query
    
    return {"detail": "ok"}


@router.get("/customers", response_model = list[Customer], tags=['customers'])
async def list_customer(session: SessionDep):
    return session.exec(select(Customer)).all()
    

db_customers : list[Customer] = []
@router.get("/customers/{customer_id}", response_model = Customer, tags=['customers'])
async def get_customer(customer_id: int):
    for customer in db_customers:
        if customer.id == customer_id:
            return customer
        
    raise HTTPException(status_code=404, detail = "Customer not found")


@router.post("/customers/{customer_id}/plans/{plan_id}")
async def subscribe_customer_to_plan(customer_id: int, plan_id: int,session: SessionDep, 
                                     plan_status: StatusEnum = Query()):
    customer_db = session.get(Customer, customer_id)
    plan_db = session.get(Plan, plan_id)

    if not customer_db or not plan_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Customer or plan does not exist")
    
    #Crear relación entre customer db y plan db
    customer_plan_db = CustomerPlan(plan_id=plan_db.id, 
                                    customer_id=customer_db.id,
                                    status = plan_status)

    session.add(customer_plan_db)
    session.commit()
    session.refresh(customer_plan_db)
    return customer_plan_db

@router.get("/customers/{customer_id}/plans")
async def check_customer_to_plan(customer_id: int, 
                                 session: SessionDep,
                                 plan_status: StatusEnum = Query()):
    customer_db = session.get(Customer, customer_id)

    if not customer_db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Customer not found")
    
    query = (select(CustomerPlan)
    .where(CustomerPlan.customer_id == customer_id)
    .where(CustomerPlan.status == plan_status))

    plans = session.exec(query).all()
    return plans