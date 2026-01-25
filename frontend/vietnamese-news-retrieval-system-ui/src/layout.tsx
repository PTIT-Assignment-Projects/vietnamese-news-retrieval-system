import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/layout/Header.tsx';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import { useCurrentApp, AppProvider } from './context/app.context.tsx';
import { App, Spin } from 'antd';
import './App.css';
import SearchHomeView from "./pages/SearchHomeView.tsx";
import About from "./pages/About.tsx";

const Root = () => {
    const { isAppLoading } = useCurrentApp();

    return (
        <>
            {isAppLoading ? (
                <div style={{
                    display: 'flex',
                    justifyContent: 'center',
                    alignItems: 'center',
                    height: '100vh',
                }}>
                    <Spin size="large" />
                </div>
            ) : (
                <Router>
                    <div className="app-container">
                        <Header />
                        <main>
                            <Routes>
                                <Route path="/" element={<Home />} />
                                <Route path="/login" element={<Login />} />
                                <Route path="/register" element={<Register />} />
                                <Route path="/search" element={<SearchHomeView />} />
                                <Route path="/about" element={<About />} />
                            </Routes>
                        </main>
                    </div>
                </Router>
            )}
        </>
    );
};

const Layout = () => {
    return (
        <AppProvider>
            <App>
                <Root />
            </App>
        </AppProvider>
    );
};

export default Layout;