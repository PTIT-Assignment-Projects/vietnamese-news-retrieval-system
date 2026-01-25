import { Card, Typography } from 'antd';

const { Title, Paragraph } = Typography;

const About = () => {
    return (
        <div style={{ padding: '20px' }}>
            <Card style={{ maxWidth: 800, margin: '0 auto' }}>
                <Typography>
                    <Title>About us</Title>
                    <Paragraph>
                        This project was created for the Information Retrieval course.
                    </Paragraph>
                    <Paragraph>
                        It was implemented by Duong Vu with help from Antigravity and community resources
                    </Paragraph>
                </Typography>
            </Card>
        </div>
    );
};

export default About;
