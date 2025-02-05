from models import Invoice
from fastapi import APIRouter

router = APIRouter()


#Con post se coge data
@router.post('/invoices', tags=['invoices'])
async def create_invoices(invoices_data: Invoice):
    return invoices_data