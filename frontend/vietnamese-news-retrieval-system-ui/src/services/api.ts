import axios from "./axios.customize";
import type { IBackendResponse, IFetchAccountResponse, ILoginResponse, IRegisterResponse } from "../types/backend";

export const logoutAPI = async () => {
    return axios.post("/api/v1/auth/logout");
};

export const registerAPI = async (name: string, email: string, password: string): Promise<IBackendResponse<IRegisterResponse>> => {
    const URL_BACKEND = "/api/v1/auth/register";
    const data = {
        name: name,
        email: email,
        password: password
    }
    return axios.post(URL_BACKEND, data);
}

export const loginAPI = async (email: string, password: string): Promise<IBackendResponse<ILoginResponse>> => {
    const URL_BACKEND = "/api/v1/auth/login";
    const data = {
        email: email,
        password: password
    }
    return axios.post(URL_BACKEND, data);
}

export const fetchAccountAPI = async (): Promise<IBackendResponse<IFetchAccountResponse>> => {
    const URL_BACKEND = "/api/v1/auth/account";
    return axios.get(URL_BACKEND);
}

export const callRefreshTokenAPI = async (): Promise<IBackendResponse<{ token: string }>> => {
    const refreshToken = typeof window !== 'undefined' ? localStorage.getItem('refresh_token') : null;
    const headers = refreshToken ? { Authorization: `Bearer ${refreshToken}` } : undefined;
    const URL_BACKEND = "/api/v1/auth/refresh";
    return axios.post(URL_BACKEND, null, { headers });
}