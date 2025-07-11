import React from 'react';
import { Empty, Typography } from 'antd';
import { FileSearchOutlined, FrownOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

const EmptyState = ({ search }) => {
    if (search) {
        return (
            <Empty
                image={<FileSearchOutlined />}
                description={
                    <>
                        <Title level={5}>No results for "{search}"</Title>
                        <Text type="secondary">Try checking your spelling or using a more general keyword.</Text>
                    </>
                }
            />
        );
    }
    return (
        <Empty
            image={<FrownOutlined />}
            description={
                <>
                    <Title level={5}>No open positions found</Title>
                    <Text type="secondary">Check back later or try refreshing the list.</Text>
                </>
            }
        />
    );
};

export default EmptyState;
