import React, { useContext } from 'react';
import { Row, Col, Card, Button, Typography } from 'antd';
import { ApartmentOutlined, GoogleOutlined } from '@ant-design/icons';
import { theme as antdTheme } from 'antd';
import {AuthContext} from '../../context/AuthContext'

const { Title, Text } = Typography;

const LoginPrompt = () => {
  const { login } = useContext(AuthContext);
  const { token } = antdTheme.useToken();

  return (
    <Row justify="center" align="middle" style={{ minHeight: 'calc(100vh - 65px)'}}>
      <Col>
        <Card style={{ width: 350, textAlign: 'center' }}>
          <ApartmentOutlined style={{ fontSize: 48, color: token.colorPrimary, marginBottom: 24 }}/>
          <Title level={3}>Welcome to engineers4hire</Title>
          <Text type="secondary" style={{ display: 'block', marginBottom: 24 }}>
            Please log in to view the latest engineering opportunities.
          </Text>
          <Button type="primary" size="large" onClick={login} block icon={<GoogleOutlined />}>
            Login with Google
          </Button>
        </Card>
      </Col>
    </Row>
  );
};

export default LoginPrompt;
