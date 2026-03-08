import { CreateTransactionPayload, Transaction } from '../types/transaction.types';

const BASE_URL = 'https://fin-app-backend-526024683416.asia-northeast1.run.app';

// ─── Auth ─────────────────────────────────────────────────────────────────────
// Temporary long-lived test token for the dummy user in the production database.
// TODO: Replace with dynamic token retrieval from SecureStore once the Google
// OAuth login flow is implemented. Pattern will be:
//   import * as SecureStore from 'expo-secure-store';
//   const token = await SecureStore.getItemAsync('auth_token');
const TEST_TOKEN = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJRTTNYTHhJWlBoNEQyZXIxamZlNCIsImV4cCI6MTc4NTY2NjkzNywidHlwZSI6ImJlYXJlciJ9.rhotNzNNUcVTnTerNKbkEzf5RtEiw0_0SxpqMgLUKhwxkUja1xjwW6IvCf3P6qd5DEWh4a7K5SyVb0k86niHeoZBb1IplS0YgrcuH7w4TO0M3LDFWMR1LPfG56dvt9isPdzsFDTswfvWVuL2rKblHjQsiJPUNSI3dEuotNKKonrQdFFesN7my99gbqbGt_AdCOKHrkyYhFN2Os023XKjCBXiDOu7C6ZjFdpBUMCoGI1nkkNdbuub9YPyFYQH_DUKkWJeMihIXsDQ5xwYhnC1Ugy0x91vo822tya8l4_i5a35eazbG4Mc1Qm4I8QAYX0O1OOMNrqV5ujL8Fz1qyqELg';

const getHeaders = () => ({
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${TEST_TOKEN}`,
});

// ─── Endpoints ────────────────────────────────────────────────────────────────

const postTransaction = async (payload: CreateTransactionPayload): Promise<Transaction> => {
    const response = await fetch(`${BASE_URL}/transactions`, {
        method: 'POST',
        headers: getHeaders(),
        body: JSON.stringify(payload),
    });

    if (!response.ok) {
        throw new Error(`POST /transactions failed: ${response.status}`);
    }

    return response.json();
};

// ─── Future endpoints ─────────────────────────────────────────────────────────
// When the backend GET /transactions response schema is finalised, add:
//
// const getTransactions = async (limit = 20, offset = 0): Promise<Transaction[]> => {
//     const response = await fetch(`${BASE_URL}/transactions?limit=${limit}&offset=${offset}`, {
//         headers: getHeaders(),
//     });
//     if (!response.ok) throw new Error(`GET /transactions failed: ${response.status}`);
//     return response.json();
// };

export default { postTransaction };