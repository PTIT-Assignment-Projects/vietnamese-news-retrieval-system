import { createContext, useContext, useState, type ReactNode } from 'react';

interface IUser {
    id: string;
    fullName: string;
    email: string;
    role: string;
}

interface AppContextType {
    user: IUser | null;
    setUser: (user: IUser | null) => void;
    isAuthenticated: boolean;
    setIsAuthenticated: (status: boolean) => void;
}

const AppContext = createContext<AppContextType | undefined>(undefined);

export const AppProvider = ({ children }: { children: ReactNode }) => {
    const [user, setUser] = useState<IUser | null>(null);
    const [isAuthenticated, setIsAuthenticated] = useState(false);

    return (
        <AppContext.Provider value={{ user, setUser, isAuthenticated, setIsAuthenticated }}>
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
