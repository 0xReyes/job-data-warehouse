import React, { useContext } from 'react';
import { Button, Space, Typography, Layout } from 'antd';
import { ReloadOutlined, LogoutOutlined, ApartmentOutlined } from '@ant-design/icons';
import { theme as antdTheme, Tooltip } from 'antd';
import {AuthContext} from '../../context/AuthContext'

const { Header } = Layout;
const { Title } = Typography;

const AppHeader = ({ onRefresh, isRefreshing }) => {
  const { isAuthenticated, logout } = useContext(AuthContext);
  const { token } = antdTheme.useToken();

  return (
    <Header style={{
      background: '#fff',
      padding: '0 24px',
      borderBottom: '1px solid #e8e8e8',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      position: 'sticky',
      top: 0,
      zIndex: 10,
    }}>
      <Title level={3} style={{ margin: 0, color: token.colorPrimary, display: 'flex', alignItems: 'center' }}>
        <ApartmentOutlined style={{ marginRight: 10 }}/>
        engineers4hire
      </Title>
      <Space>
        {isAuthenticated && (
          <>
            <Button icon={<ReloadOutlined />} onClick={onRefresh} loading={isRefreshing}>
              Refresh Jobs
            </Button>
            <Tooltip title="Logout">
              <Button danger type="text" icon={<LogoutOutlined />} onClick={logout} />
            </Tooltip>
          </>
        )}
      </Space>
    </Header>
  );
};

export default AppHeader;
