export type TransactionType = 'income' | 'expense' | 'subscription';

export interface Transaction {
    id: number;
    currency: string;
    amount: number;
    transaction_type: TransactionType;
    category: string | null;
    description: string | null;
    business_name: string | null;
    payment_method: string | null;
    exchange_rate: number | null;
    occurred_at: string;
}

export interface Category {
    id: number;
    title: string;
    amount: number;
}

export interface CreateTransactionPayload {
    amount: number;
    exchange_rate: number | null;
    currency: string;
    transaction_type: TransactionType;
    category: string | null;
    description: string | null;
    business_name: string | null;
    payment_method: string | null;
}

