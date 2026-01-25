import {Link, useNavigate} from 'react-router-dom';
import { Button, Form, Input, Card, message } from 'antd';
import { LockOutlined, UserOutlined, MailOutlined } from '@ant-design/icons';
import { registerAPI } from '../services/api.ts';

type FieldType = {
    name: string;
    email: string;
    password: string;
}

const Register = () => {
    const navigate = useNavigate();

    const onFinish = async (values: FieldType) => {
        const { name, email, password } = values;
        const res: any = await registerAPI(name, email, password);
        if (res.data) {
            message.success('Registration successful! Please login.');
            navigate('/login');
        } else {
            message.error(res.message || 'Registration failed');
        }
    };

    return (
        <div style={{ display: 'flex', justifyContent: 'center', marginTop: '50px' }}>
            <Card title="Register" style={{ width: 400 }}>
                <Form
                    name="register_form"
                    onFinish={onFinish}
                    layout="vertical"
                >
                    <Form.Item
                        name="name"
                        label="Full Name"
                        rules={[{ required: true, message: 'Please input your full name!' }]}
                    >
                        <Input prefix={<UserOutlined />} placeholder="Full Name" />
                    </Form.Item>
                    <Form.Item
                        name="email"
                        label="Email"
                        rules={[{ required: true, message: 'Please input your Email!', type: 'email' }]}
                    >
                        <Input prefix={<MailOutlined />} placeholder="Email" />
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
                            Register
                        </Button>
                        <div style={{ marginTop: '10px', textAlign: 'center' }}>
                            Already have an account? <Link to="/login">Login Here</Link>;
                        </div>
                    </Form.Item>
                </Form>
            </Card>
        </div>
    );
};

export default Register;
