import React, { useState, useEffect, useCallback, useContext } from 'react';
import {
  Button,
  Input,
  Tag,
  Table,
  Space,
  Typography,
  Card,
  Row,
  Col,
  Layout,
  Spin,
  Modal,
  Form,
  message
} from 'antd';

import {
  SearchOutlined,
  EnvironmentOutlined,
  StarFilled,
  ClockCircleOutlined,
  ReloadOutlined,
  LinkOutlined,
  EditOutlined,
  FileTextOutlined,
  UserOutlined
} from '@ant-design/icons';
import { AuthContext } from './context/AuthContext';
import { AuthProvider } from './context/AuthProvider';

const { Header, Content } = Layout;
const { Title, Text } = Typography;
const { TextArea } = Input;

const CoverLetterModal = ({ visible, onClose, job, onSave, initialData }) => {
  const [form] = Form.useForm();

  useEffect(() => {
    if (visible) initialData ? form.setFieldsValue(initialData) : form.resetFields();
  }, [visible, initialData, form]);

  const handleSave = () => form.validateFields()
    .then(values => {
      onSave(job.id, values);
      onClose();
      message.success('Application notes saved!');
    })
    .catch(error => console.error('Form validation failed:', error));

  return (
    <Modal
      title={`Application for ${job?.title} at ${job?.company}`}
      open={visible}
      onCancel={onClose}
      onOk={handleSave}
      okText="Save"
      width={800}
    >
      <Form form={form} layout="vertical">
        <Form.Item name="coverLetter" label="Cover Letter" rules={[{ required: true, message: 'Please write your cover letter' }]}>
          <TextArea rows={8} placeholder="Write your personalized cover letter..." />
        </Form.Item>
        <Form.Item name="notes" label="Additional Notes">
          <TextArea rows={4} placeholder="Add notes (salary, follow-up, etc.)" />
        </Form.Item>
      </Form>
    </Modal>
  );
};

const AppHeader = ({ onRefresh, isRefreshing }) => {
  const { isAuthenticated, logout } = useContext(AuthContext);

  return (
    <Header style={{ background: 'linear-gradient(135deg, #667eea, #764ba2)', padding: '0 24px', boxShadow: '0 2px 8px rgba(0,0,0,0.1)' }}>
      <Row justify="space-between" align="middle" style={{ height: '100%' }}>
        <Col>
          <Title level={2} style={{ margin: 0, color: '#fff' }}>engineers4hire</Title>
        </Col>
        <Col>
          <Space>
            <Button type="primary" ghost icon={<ReloadOutlined />} onClick={onRefresh} loading={isRefreshing}>
              Refresh Jobs
            </Button>
            {isAuthenticated && <Button ghost icon={<UserOutlined />} onClick={logout}>Logout</Button>}
          </Space>
        </Col>
      </Row>
    </Header>
  );
};

function App() {
  const { isAuthenticated, loading, login, getJobData } = useContext(AuthContext);
  const [jobs, setJobs] = useState([]);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [search, setSearch] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [applicationData, setApplicationData] = useState({});

  const loadJobs = useCallback(async () => {
    if (isRefreshing) return;
    setIsRefreshing(true);
    try {
      const response = await getJobData();
      const rawData = response.data;

      if (Array.isArray(rawData)) {
        const transformedData = rawData.map((item, index) => ({
          id: item.link || index,
          company: item.company_name || 'Unknown Company',
          title: item.title,
          tags: [],
          location: 'Remote Available',
          posted: item.date_fetched,
          source: item.source || (item.link ? new URL(item.link).hostname : 'unknown.com'),
          type: 'Full-time',
          link: item.link,
          snippet: item.snippet,
          featured: false
        }));
        setJobs(transformedData);
      } else {
        setJobs([]);
      }
    } catch (error) {
      console.error('Error loading jobs:', error);
      setJobs([]);
    }
    setIsRefreshing(false);
  }, [getJobData]);

  useEffect(() => { loadJobs(); }, [loadJobs]);

  useEffect(() => {
    if (search) {
      const searchTerm = search.toLowerCase();
      setJobs(prev => prev.filter(job =>
        job.title?.toLowerCase().includes(searchTerm) ||
        job.company?.toLowerCase().includes(searchTerm) ||
        job.snippet?.toLowerCase().includes(searchTerm)
      ));
    } else {
      loadJobs();
    }
  }, [search, loadJobs]);

  const handleEditApplication = useCallback(job => {
    setSelectedJob(job);
    setModalVisible(true);
  }, []);

  const handleSaveApplication = useCallback((jobId, data) => {
    setApplicationData(prev => ({ ...prev, [jobId]: data }));
  }, []);

  const columns = [
    {
      title: 'Company & Role',
      key: 'job',
      render: (_, record) => (
        <>
          <Text strong style={{ fontSize: '16px' }}>{record.company}</Text>
          {record.featured && <Tag color="gold" icon={<StarFilled />}>Featured</Tag>}
          <Title level={5} style={{ margin: 0, color: '#1890ff', fontWeight: 'normal' }}>{record.title}</Title>
        </>
      ),
      width: '40%'
    },
    {
      title: 'Details',
      key: 'details',
      render: (_, record) => (
        <>
          <Text type="secondary"><EnvironmentOutlined /> {record.location}</Text>
          <Text type="secondary" style={{ marginLeft: '16px' }}><ClockCircleOutlined /> {record.posted}</Text>
        </>
      ),
      width: '30%'
    },
    {
      title: 'Source',
      dataIndex: 'source',
      key: 'source',
      render: source => <Tag color="purple">{source}</Tag>,
      width: '15%'
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button type="primary" size="small" icon={<LinkOutlined />} onClick={e => { e.stopPropagation(); window.open(record.link, '_blank'); }}>
            Apply
          </Button>
          <Button size="small" icon={applicationData[record.id] ? <FileTextOutlined /> : <EditOutlined />}
            onClick={e => { e.stopPropagation(); handleEditApplication(record); }}
            type={applicationData[record.id] ? 'default' : 'dashed'}
          >
            {applicationData[record.id] ? 'Edit' : 'Add'} Notes
          </Button>
        </Space>
      ),
      width: '15%'
    }
  ];

  const display = useCallback(() => (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <AppHeader onRefresh={loadJobs} isRefreshing={isRefreshing} />
      <Content style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto', width: '100%' }}>
        <Card style={{ marginBottom: '24px', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
          <Row gutter={[16, 16]}>
            <Col xs={24}>
              <Input size="large" placeholder="Search by company, title, or description..." prefix={<SearchOutlined />}
                value={search} onChange={e => setSearch(e.target.value)} style={{ borderRadius: '8px' }} />
            </Col>
          </Row>
        </Card>
        <Card style={{ borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
          <Title level={4} style={{ margin: 0 }}>Job Listings ({jobs.length})</Title>
          <Table
            columns={columns}
            dataSource={jobs}
            rowKey="id"
            loading={isRefreshing}
            pagination={{ pageSize: 10, showSizeChanger: false, showQuickJumper: true, showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} jobs` }}
            expandable={{ expandedRowRender: record => <p style={{ margin: 0 }}>{record.snippet}</p>, rowExpandable: record => record.snippet }}
            style={{ borderRadius: '8px' }}
          />
        </Card>
        <CoverLetterModal
          visible={modalVisible}
          onClose={() => setModalVisible(false)}
          job={selectedJob}
          onSave={handleSaveApplication}
          initialData={selectedJob ? applicationData[selectedJob.id] : undefined}
        />
      </Content>
    </Layout>
  ), [jobs, isRefreshing, search, modalVisible, selectedJob, applicationData, loadJobs, handleEditApplication, handleSaveApplication]);

  if (loading) {
    return (
      <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
        <AppHeader onRefresh={loadJobs} isRefreshing={isRefreshing} />
        <Content style={{ padding: '48px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <Spin size="large" />
          <Text type="secondary" style={{ fontSize: '16px', marginTop: '16px' }}>Loading application...</Text>
        </Content>
      </Layout>
    );
  }

  if (!isAuthenticated) {
    return (
      <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
        <AppHeader onRefresh={loadJobs} isRefreshing={isRefreshing} />
        <Content style={{ padding: '48px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <Card style={{ width: 400, textAlign: 'center' }}>
            <Title level={3}>Welcome to engineers4hire</Title>
            <Text type="secondary">Please authenticate to view job listings</Text>
            <Button type="primary" size="large" onClick={login} style={{ marginTop: '24px' }}>Login</Button>
          </Card>
        </Content>
      </Layout>
    );
  }

  return display();
}

export default function AppWrapper() {
  return <AuthProvider><App /></AuthProvider>;
}