import React, { useEffect } from 'react';
import { Typography, Form, Button, Card, Input } from 'antd';
import { SearchOutlined } from '@ant-design/icons'; 
const JobSearch = ({ search, setSearch, resultsCount }) => (
  <Card style={{ marginBottom: 24 }}>
    <Input
      size="large"
      placeholder="Search by role, company, or keyword..."
      prefix={<SearchOutlined style={{ color: '#aaa' }} />}
      value={search}
      onChange={e => setSearch(e.target.value)}
      allowClear
    />
    <Typography.Text type="secondary" style={{ marginTop: 8, display: 'block' }}>
      Showing {resultsCount} {resultsCount === 1 ? 'job' : 'jobs'}
    </Typography.Text>
  </Card>
);

export default JobSearch