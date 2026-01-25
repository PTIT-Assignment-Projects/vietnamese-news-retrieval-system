import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Header from './components/layout/Header.tsx';
import Home from './pages/Home';
import Login from './pages/Login';
import Register from './pages/Register';
import { AppProvider } from './context/app.context.tsx';
import { App } from 'antd';
import './App.css';
import SearchHomeView from "./pages/SearchHomeView.tsx";
import About from "./pages/About.tsx";

const Layout = () => {
    return (
        <AppProvider>
            <App>
                <Router>
                    <div className="app-container">
                        <Header />
                        <main>
                            <Routes>
                                <Route path="/" element={<Home />} />
                                <Route path="/login" element={<Login />} />
                                <Route path="/register" element={<Register />} />
                                <Route path="/search" element={<SearchHomeView/>} />
                                <Route path="/about" element={<About/>} />
                            </Routes>
                        </main>
                    </div>
                </Router>
            </App>
        </AppProvider>
    );
};

export default Layout;