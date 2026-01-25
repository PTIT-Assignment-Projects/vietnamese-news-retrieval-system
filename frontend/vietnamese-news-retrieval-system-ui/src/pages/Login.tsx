import { useNavigate, Link } from 'react-router-dom';
import { useCurrentApp } from '../context/app.context.tsx';
import { Button, Form, Input, Card, message } from 'antd';
import { LockOutlined, UserOutlined } from '@ant-design/icons';
import { loginAPI } from '../services/api.ts';

const Login = () => {
    const { setUser, setIsAuthenticated } = useCurrentApp();
    const navigate = useNavigate();

    const onFinish = async (values: any) => {
        const { email, password } = values;
        const res = await loginAPI(email, password);

        if (res.data) {
            const payload = res.data;
            const loggedUser = {
                id: payload.id,
                name: payload.name,
                email: payload.email,
            };

            setUser(loggedUser);
            setIsAuthenticated(true);
            localStorage.setItem('access_token', payload.token);
            localStorage.setItem('refresh_token', payload.refresh_token);

            message.success('Login successfully!');
            navigate('/');
        } else {
            const errorRes = res as any;
            message.error(errorRes.error || 'Login failed');
        }
    };

    return (
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: '50px' }}>
            <Card title="Login" style={{ width: 400 }}>
                <Form
                    name="login_form"
                    initialValues={{ remember: true }}
                    onFinish={onFinish}
                    layout="vertical"
                >
                    <Form.Item
                        name="email"
                        label="Email"
                        rules={[{ required: true, message: 'Please input your Email!', type: 'email' }]}
                    >
                        <Input prefix={<UserOutlined />} placeholder="Email" />
                    </Form.Item>
                    <Form.Item
                        name="password"
                        label="Password"
                        rules={[{ required: true, message: 'Please input your Password!' }]}
                    >
                        <Input.Password
                            prefix={<LockOutlined />}
                            placeholder="Password"
                        />
                    </Form.Item>

                    <Form.Item>
                        <Button type="primary" htmlType="submit" style={{ width: '100%' }}>
                            Log in
                        </Button>
                        <div style={{ marginTop: '10px', textAlign: 'center' }}>
                            Or <Link to="/register">register now!</Link>
                        </div>
                    </Form.Item>
                </Form>
            </Card>
        </div>
    );
};

export default Login;