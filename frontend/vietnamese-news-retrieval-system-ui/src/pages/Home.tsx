import { Card, Typography } from 'antd';

const { Title, Paragraph } = Typography;

const Home = () => {
    return (
        <div style={{ padding: '20px' }}>
            <Card style={{ maxWidth: 800, margin: '0 auto' }}>
                <Typography>
                    <Title>Welcome to Vietnamese News Retrieval</Title>
                    <Paragraph>
                        This is a system designed to search and retrieve Vietnamese news articles efficiently.
                    </Paragraph>
                    <Paragraph>
                        Navigate through the menu to start searching or manage your account.
                    </Paragraph>
                </Typography>
            </Card>
        </div>
    );
};

export default Home;
