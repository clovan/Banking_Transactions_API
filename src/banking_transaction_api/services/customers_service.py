import pandas as pd
from typing import Dict, Any, List, Optional
from banking_transaction_api.data_loader import DataLoader


class CustomersService:
    """Service for customer data retrieval and analysis."""

    def __init__(self):
        # Initialize the data loader singleton
        self.data_loader = DataLoader()

    def _format_customer_id(self, client_id: int) -> str:
        """
        Format numeric client_id to string format matching spec (e.g., "C1231006815").

        Parameters
        ----------
        client_id : int
            Numeric client identifier.

        Returns
        -------
        str
            Formatted customer ID with "C" prefix.
        """
        return f"C{client_id}"

    def _parse_customer_id(self, customer_id: str) -> Optional[int]:
        """
        Parse string customer ID to extract the numeric part.

        Parameters
        ----------
        customer_id : str
            Customer ID string (e.g., "C1231006815").

        Returns
        -------
        Optional[int]
            Numeric client ID, or None if parsing fails.
        """
        try:
            # Remove 'C' prefix (case insensitive) if present
            if customer_id.lower().startswith('c'):
                return int(customer_id[1:])
            return int(customer_id)
        except (ValueError, TypeError):
            return None

    def get_customers(self, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        """
        Get a paginated list of customers from the users dataset.

        Parameters
        ----------
        page : int
            Page number (1-indexed).
        limit : int
            Number of customers per page.

        Returns
        -------
        Dict[str, Any]
            Pagination metadata and the list of formatted customer IDs.
        """
        customers_df = self.data_loader.users
        if customers_df is None or customers_df.empty:
            return {"page": page, "limit": limit, "total": 0, "customers": []}

        # Use the 'id' column from users_data.csv
        unique_customers = customers_df['id'].unique()
        total_customers = len(unique_customers)

        # Pagination logic
        start = (page - 1) * limit
        end = start + limit
        page_clients = unique_customers[start:end]

        customers_list = [
            {"id": self._format_customer_id(int(cid))}
            for cid in page_clients
        ]

        return {
            "page": page,
            "limit": limit,
            "total": total_customers,
            "customers": customers_list
        }

    def get_customer_profile(self, customer_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a synthetic customer profile including transaction stats and fraud status.

        Parameters
        ----------
        customer_id : str
            Customer ID (e.g., "C1231006815").

        Returns
        -------
        Optional[Dict[str, Any]]
            Profile data or None if the customer is not found.
        """
        transactions = self.data_loader.transactions
        numeric_id = self._parse_customer_id(customer_id)

        if numeric_id is None or transactions is None:
            return None

        # Filter transactions for this specific client
        user_txs = transactions[transactions['client_id'] == numeric_id]

        if user_txs.empty:
            return None

        tx_count = len(user_txs)
        avg_amount = round(user_txs['amount'].mean(), 2) if tx_count > 0 else 0.0

        # Fraud check based on the is_fraud column created in DataLoader
        has_fraud = False
        if 'is_fraud' in user_txs.columns:
            has_fraud = int(user_txs['is_fraud'].sum()) > 0

        return {
            "id": self._format_customer_id(numeric_id),
            "transactions_count": tx_count,
            "avg_amount": float(avg_amount),
            "fraudulent": bool(has_fraud)
        }

    def get_top_customers(self, n: int = 10) -> List[Dict[str, Any]]:
        """
        Get top customers ranked by total transaction volume.

        Parameters
        ----------
        n : int
            Number of top customers to return.

        Returns
        -------
        List[Dict[str, Any]]
            List of top customers with volume and transaction counts.
        """
        transactions = self.data_loader.transactions
        if transactions is None:
            return []

        # Grouping by client_id to calculate metrics
        stats = transactions.groupby('client_id').agg(
            total_volume=('amount', 'sum'),
            transactions_count=('amount', 'count') # Using amount to count rows
        ).sort_values('total_volume', ascending=False).head(n)

        results = []
        for client_id, row in stats.iterrows():
            results.append({
                "id": self._format_customer_id(int(client_id)),
                "total_volume": round(float(row['total_volume']), 2),
                "transactions_count": int(row['transactions_count'])
            })

        return results