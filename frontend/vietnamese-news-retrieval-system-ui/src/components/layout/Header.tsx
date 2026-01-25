import { useCurrentApp } from "../../context/app.context.tsx";
import { Link, useNavigate } from "react-router-dom";
import { logoutAPI } from "../../services/api.ts";
import { App, Menu, type MenuProps } from "antd";
import {
    AlertOutlined,
    AliwangwangOutlined,
    ExclamationOutlined,
    HomeOutlined,
    LoginOutlined,
} from "@ant-design/icons";
import { useState } from "react";
import type {MenuItemType} from "antd/lib/menu/interface";

// Define proper types for menu items
// interface IMenuItem {
//     label: React.ReactNode;
//     key: string;
//     icon?: React.ReactNode;
//     children?: IMenuItem[];
//     disabled?: boolean;
// };

const AppHeader = () => {
    const { message, notification } = App.useApp();
    const { user, setUser, setIsAuthenticated } = useCurrentApp();
    const navigate = useNavigate();
    const [current, setCurrent] = useState<string>("");

    const onClick: MenuProps['onClick'] = (e) => {
        setCurrent(e.key);
    };

    const handleLogout = async () => {
        try {
            const res = await logoutAPI();
            if (res.statusCode === 200) {
                localStorage.removeItem("access_token");
                setUser(null);
                setIsAuthenticated(false);
                message.success("Logout successfully");
                navigate("/");
            } else {
                notification.error({
                    message: "Log out failed!",
                    description: res.message || "Unknown error",
                });
            }
        } catch (err: any) {
            notification.error({
                message: "Log out failed!",
                description: err?.response?.data?.message || "Unknown error",
            });
        }
    };

    const items: MenuItemType[] = [
        {
            label: <Link to={"/"}>Home</Link>,
            key: "home",
            icon: <HomeOutlined />,
        },
        {
            label: <Link to={"/search"}>Search</Link>, // Changed from backup to search
            key: "search",
            icon: <ExclamationOutlined />,
        },
        ...(!user?.id ? [
            {
                label: <Link to={"/login"}>Login</Link>,
                key: "login",
                icon: <LoginOutlined />,
                
            },
            {
                label: <Link to={"/register"}>Register</Link>,
                key: "register",
                icon: <LoginOutlined />,
            },
        ] : []),
        ...(user?.id ? [
            {
                label: `Welcome ${user?.fullName}`,
                key: "setting",
                icon: <AliwangwangOutlined />,
                children: [
                    {
                        label: <span onClick={() => handleLogout()}>Logout</span>,
                        key: "logout",
                    },
                ],
            },
        ] : []),
        {
            label: <Link to={"/about"}>About us</Link>, // Changed from backup to search
            key: "about",
            icon: <AlertOutlined />,
        }
    ] as MenuItemType[];

    if (user?.role === 'ADMIN') {
        items.unshift({
            label: <Link to='/admin'>Admin Dashboard</Link>,
            key: 'admin',
        });
    }

    return (
        <Menu onClick={onClick} selectedKeys={[current]} mode="horizontal" items={items} />
    );
};

export default AppHeader;
