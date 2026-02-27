export interface Transaction {
    id: number,
    currency: string,
    amount: number,
    category: string,
    description: string,
    occurred_at: string,
}

export interface Category {
    id: number,
    title: string,
    amount: number,
}

