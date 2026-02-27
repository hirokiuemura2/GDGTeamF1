import * as SecureStore from 'expo-secure-store'
import { NewUser, User } from '../types/authService.types'


const baseURL = 'https://fin-app-backend-526024683416.asia-northeast1.run.app/'
const AUTH_TOKEN_KEY = 'auth_token'
const REFRESH_TOKEN_KEY = 'refresh_token'

const signUp = async (newUser: NewUser) => {
    const response = await fetch(baseURL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(newUser)
    })
    if (!response.ok) {
        throw new Error(`Response status: ${response.status}`)
    }

    const result = await response.json()

    if (result.access_token) {
        await SecureStore.setItemAsync(AUTH_TOKEN_KEY, result.access_token)
    }
    if (result.refresh_token) {
        await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, result.refresh_token)
    }
    return result
}


const login = async (user: User) => {
    const response = await fetch(baseURL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(user)
    })
    if(!response.ok) {
        throw new Error(`Response status: ${response.status}`)
    }

    const result = await response.json()

    if(result.access_token) {
        await SecureStore.setItemAsync(AUTH_TOKEN_KEY, result.access_token)
    }
    if(result.refresh) {
        await SecureStore.setItemAsync(REFRESH_TOKEN_KEY, result.refresh_token)
    }
}
export default { signUp, login}