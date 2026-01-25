import { createContext, useContext, useEffect, useState, type ReactNode } from 'react';

import type { IUser } from '../types/backend';
import { fetchAccountAPI, callRefreshTokenAPI } from '../services/api';

interface AppContextType {
    user: IUser | null;
    setUser: (user: IUser | null) => void;
    isAuthenticated: boolean;
    setIsAuthenticated: (status: boolean) => void;
    isAppLoading: boolean;
    setIsAppLoading: (loading: boolean) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<IUser | null>(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [isAppLoading, setIsAppLoading] = useState(true);

    const getAccount = async () => {
        const accessToken = localStorage.getItem('access_token');
        const refreshToken = localStorage.getItem('refresh_token');

        if (!accessToken && !refreshToken) {
            setIsAppLoading(false);
            return;
        }

        const res = await fetchAccountAPI();
        if (res && res.data) {
            setUser(res.data);
            setIsAuthenticated(true);
        } else {
            // If primary fetch fails, try to refresh the token
            if (refreshToken) {
                const refreshRes = await callRefreshTokenAPI();
                if (refreshRes && refreshRes.data && refreshRes.data.token) {
                    const newToken = refreshRes.data.token;
                    localStorage.setItem('access_token', newToken);

                    // Retry fetching account with new token
                    const retryRes = await fetchAccountAPI();
                    if (retryRes && retryRes.data) {
                        setUser(retryRes.data);
                        setIsAuthenticated(true);
                    }
                } else {
                    // Refresh token also invalid or expired
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    console.log("Session expired, please login again");
                }
            }
        }
        setIsAppLoading(false);
    }

    useEffect(() => {
        getAccount();
    }, []);

    return (
        <AppContext.Provider value={{
            user, setUser,
            isAuthenticated, setIsAuthenticated,
            isAppLoading, setIsAppLoading
        }}>
            {children}
        </AppContext.Provider>
    );
};

export const useCurrentApp = () => {
    const context = useContext(AppContext);
    if (context === undefined) {
        throw new Error('useCurrentApp must be used within an AppProvider');
    }
    return context;
};
