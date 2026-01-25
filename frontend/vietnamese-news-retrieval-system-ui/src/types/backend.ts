export interface IBackendResponse<T> {
    data: T;
}

export interface IBackendError {
    error: string;
    status: number;
}

export interface IUser {
    id: string;
    email: string;
    name: string;
    role?: string;
    created_at?: string;
    updated_at?: string;
}

export interface ILoginResponse {
    id: string;
    email: string;
    name: string;
    token: string;
    refresh_token: string;
    created_at: string;
    updated_at: string;
}

export interface IFetchAccountResponse {
    id: string;
    email: string;
    name: string;
    created_at: string;
    updated_at: string;
}

export interface IRegisterResponse {
    id: string;
    email: string;
    name: string;
    created_at: string;
    updated_at: string;
}
