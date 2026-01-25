import axios, { type InternalAxiosRequestConfig, type AxiosResponse, type AxiosError } from "axios";

/**
 * Custom Axios instance with interceptors for JWT injection and response handling.
 */
const instance = axios.create({
    baseURL: import.meta.env.VITE_BACKEND_URL as string
});

// Request Interceptor: Inject JWT token from localStorage
instance.interceptors.request.use(
    (config: InternalAxiosRequestConfig) => {
        if (typeof window !== "undefined") {
            const accessToken = window.localStorage.getItem('access_token');
            if (accessToken && !config.headers.Authorization) {
                config.headers.Authorization = `Bearer ${accessToken}`;
            }
        }
        return config;
    },
    (error: AxiosError) => {
        return Promise.reject(error);
    }
);

// Response Interceptor: Simplify response data and handle errors
instance.interceptors.response.use(
    (response: AxiosResponse) => {
        // Log for debugging (as requested)
        console.log("Check axios response:", response);

        // Return only data if it follows the common { data: ... } pattern
        // Otherwise return the whole response
        if (response.data && response.data.data) {
            return response.data;
        }
        if (response.data === "") {
            return response;
        }
        return response.data ?? response;
    },
    (error: AxiosError) => {
        // If the server returned an error response with data, return that data
        if (error.response && error.response.data) {
            return error.response.data;
        }
        return Promise.reject(error);
    }
);

export default instance;
