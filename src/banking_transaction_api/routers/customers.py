from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from banking_transaction_api.services.customers_service import CustomersService

router = APIRouter(prefix="/api/customers", tags=["Customers"])
service = CustomersService()


@router.get("")
def get_customers(page: int = 1, limit: int = 10) -> Dict[str, Any]:
    """
    Paginated list of customers (extracted from original transaction data).

    Parameters
    ----------
    page : int
        Page number (default: 1)
    limit : int
        Number of items per page (default: 10)

    Returns
    -------
    Dict[str, Any]
        Paginated list of customers
    """
    return service.get_customers(page, limit)


@router.get("/top")
def get_top_customers(n: int = 10) -> List[Dict[str, Any]]:
    """
    Top customers ranked by total transaction volume.

    Parameters
    ----------
    n : int
        Number of top customers to return (default: 10)

    Returns
    -------
    List[Dict[str, Any]]
        List of top customers by transaction volume
    """
    return service.get_top_customers(n)


@router.get("/{customer_id}")
def get_customer(customer_id: str) -> Dict[str, Any]:
    """
    Synthetic customer profile including transaction count, average balance, 
    and fraud involvement.

    Parameters
    ----------
    customer_id : str
        Customer ID (e.g., "C1231006815")

    Returns
    -------
    Dict[str, Any]
        Customer profile with id, transactions_count, avg_amount, and fraud status
    """
    customer = service.get_customer_profile(customer_id)
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer