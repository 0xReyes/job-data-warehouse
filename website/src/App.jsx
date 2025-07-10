import React, { useState, useEffect, useCallback, useContext } from 'react';
import { 
  Button, 
  Select,  
  Input, 
  Tag, 
  Avatar, 
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

// Cover Letter Modal Component
const CoverLetterModal = ({ visible, onClose, job, onSave, initialData }) => {
  const [form] = Form.useForm();
  
  useEffect(() => {
    if (visible && initialData) {
      form.setFieldsValue(initialData);
    } else if (visible) {
      form.resetFields();
    }
  }, [visible, initialData, form]);

  const handleSave = () => {
    form.validateFields().then(values => {
      onSave(job.id, values);
      onClose();
      message.success('Application notes saved!');
    }).catch(error => {
      console.error('Form validation failed:', error);
    });
  };

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
        <Form.Item
          name="coverLetter"
          label="Cover Letter"
          rules={[{ required: true, message: 'Please write your cover letter' }]}
        >
          <TextArea
            rows={8}
            placeholder="Write your personalized cover letter for this position..."
          />
        </Form.Item>
        <Form.Item
          name="notes"
          label="Additional Notes"
        >
          <TextArea
            rows={4}
            placeholder="Add any notes about this application (salary expectations, follow-up dates, etc.)"
          />
        </Form.Item>
      </Form>
    </Modal>
  );
};

// Header Component
const AppHeader = ({ onRefresh, isRefreshing }) => {
  const { isAuthenticated, logout } = useContext(AuthContext);

  return (
    <Header style={{ 
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', 
      padding: '0 24px',
      boxShadow: '0 2px 8px rgba(0,0,0,0.1)'
    }}>
      <Row justify="space-between" align="middle" style={{ height: '100%' }}>
        <Col>
          <Title level={2} style={{ margin: 0, color: '#fff' }}>
            engineers4hire
          </Title>
        </Col>
        <Col>
          <Space>
            <Button 
              type="primary"
              ghost
              icon={<ReloadOutlined />} 
              onClick={onRefresh}
              loading={isRefreshing}
            >
              Refresh Jobs
            </Button>
            {isAuthenticated && (
              <Button 
                ghost
                icon={<UserOutlined />}
                onClick={logout}
              >
                Logout
              </Button>
            )}
          </Space>
        </Col>
      </Row>
    </Header>
  );
};

// Main App Component
function App() {
  const {
    isAuthenticated,
    loading,
    login,
    getJobData,
  } = useContext(AuthContext);
  const [jobs, setJobs] = useState([]);
  const [allJobs, setAllJobs] = useState([]);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedFunction, setSelectedFunction] = useState('all');
  const [selectedLocation, setSelectedLocation] = useState('all');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedSource, setSelectedSource] = useState('all');
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [applicationData, setApplicationData] = useState({});

  // Get unique filter options from current jobs
  const getUniqueOptions = useCallback((key) => {
    const values = allJobs.map(job => job[key]).filter(val => val != null);
    return [...new Set(values)].sort();
  }, [allJobs]);

  const loadJobs = useCallback(async () => {
    if (!isAuthenticated) return;
    
    setIsRefreshing(true);
    try {
      const response = await getJobData();
      if (response?.data) {
        setAllJobs(response.data);
      }
    } catch (error) {
      console.error('Error loading jobs:', error);
      message.error('Failed to load jobs. Please try again.');
    } finally {
      setIsRefreshing(false);
    }
  }, [isAuthenticated, getJobData]);

  useEffect(() => {
    if (isAuthenticated && allJobs.length === 0) {
      loadJobs();
    }
  }, [isAuthenticated, loadJobs, allJobs.length]);

  useEffect(() => {
    let filtered = allJobs;

    if (search) {
      const searchTerm = search.toLowerCase();
      filtered = filtered.filter(job =>
        (job.title && job.title.toLowerCase().includes(searchTerm)) ||
        (job.company && job.company.toLowerCase().includes(searchTerm)) ||
        (job.tags && job.tags.some(tag => tag.toLowerCase().includes(searchTerm)))
      );
    }

    if (selectedFunction !== 'all') {
      filtered = filtered.filter(job =>
        job.tags && job.tags.some(tag => tag.toLowerCase().includes(selectedFunction.toLowerCase()))
      );
    }

    if (selectedLocation !== 'all') {
      filtered = filtered.filter(job =>
        job.location && job.location.toLowerCase().includes(selectedLocation.toLowerCase())
      );
    }

    if (selectedType !== 'all') {
      filtered = filtered.filter(job =>
        job.type && job.type.toLowerCase() === selectedType.toLowerCase()
      );
    }

    if (selectedSource !== 'all') {
      filtered = filtered.filter(job =>
        job.source && job.source.toLowerCase() === selectedSource.toLowerCase()
      );
    }

    setJobs(filtered);
  }, [allJobs, search, selectedFunction, selectedLocation, selectedType, selectedSource]);

  const handleEditApplication = useCallback((job) => {
    setSelectedJob(job);
    setModalVisible(true);
  }, []);

  const handleSaveApplication = useCallback((jobId, data) => {
    setApplicationData(prev => ({
      ...prev,
      [jobId]: data
    }));
  }, []);

  const columns = [
    {
      title: 'Company & Role',
      key: 'job',
      render: (_, record) => (
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <Avatar 
            src={`https://ui-avatars.com/api/?name=${record.company}&background=667eea&color=fff&size=40`}
            size={40} 
            shape="square" 
            style={{ borderRadius: '8px' }}
          />
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
              <Text strong style={{ fontSize: '16px' }}>{record.company}</Text>
              {record.featured && <Tag color="gold" icon={<StarFilled />}>Featured</Tag>}
            </div>
            <Title level={5} style={{ margin: 0, color: '#1890ff' }}>{record.title}</Title>
          </div>
        </div>
      ),
      width: '40%'
    },
    {
      title: 'Details',
      key: 'details',
      render: (_, record) => (
        <div>
          <Space wrap style={{ marginBottom: '8px' }}>
            {record.tags && record.tags.map(tag => (
              <Tag key={tag} color="blue" style={{ borderRadius: '12px' }}>{tag}</Tag>
            ))}
          </Space>
          <div>
            <Text type="secondary">
              <EnvironmentOutlined /> {record.location}
            </Text>
            <Text type="secondary" style={{ marginLeft: '16px' }}>
              <ClockCircleOutlined /> {record.posted}
            </Text>
          </div>
        </div>
      ),
      width: '30%'
    },
    {
      title: 'Source',
      dataIndex: 'source',
      key: 'source',
      render: (source) => <Tag color="purple">{source}</Tag>,
      width: '15%'
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space>
          <Button
            type="primary"
            size="small"
            icon={<LinkOutlined />}
            onClick={(e) => {
              e.stopPropagation();
              window.open(record.link, '_blank');
            }}
          >
            Apply
          </Button>
          <Button
            size="small"
            icon={applicationData[record.id] ? <FileTextOutlined /> : <EditOutlined />}
            onClick={(e) => {
              e.stopPropagation();
              handleEditApplication(record);
            }}
            type={applicationData[record.id] ? "default" : "dashed"}
          >
            {applicationData[record.id] ? 'Edit' : 'Add'} Notes
          </Button>
        </Space>
      ),
      width: '15%'
    }
  ];

  if (loading) {
    return (
      <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
        <AppHeader onRefresh={loadJobs} isRefreshing={isRefreshing} />
        <Content style={{ padding: '48px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <div style={{ textAlign: 'center' }}>
            <Spin size="large" />
            <div style={{ marginTop: '16px' }}>
              <Text type="secondary" style={{ fontSize: '16px' }}>Loading application...</Text>
            </div>
          </div>
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
            <div style={{ marginTop: '24px' }}>
              <Button type="primary" size="large" onClick={login}>
                Login
              </Button>
            </div>
          </Card>
        </Content>
      </Layout>
    );
  }

  return (
    <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
      <AppHeader onRefresh={loadJobs} isRefreshing={isRefreshing} />
      <Content style={{ padding: '24px', maxWidth: '1400px', margin: '0 auto', width: '100%' }}>
        <Card style={{ marginBottom: '24px', borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
          <Row gutter={[16, 16]}>
            <Col xs={24} md={8}>
              <Input
                size="large"
                placeholder="Search jobs or companies..."
                prefix={<SearchOutlined />}
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                style={{ borderRadius: '8px' }}
              />
            </Col>
            <Col xs={12} md={4}>
              <Select 
                size="large"
                value={selectedFunction}
                onChange={setSelectedFunction}
                style={{ width: '100%' }}
              >
                <Select.Option value="all">All Functions</Select.Option>
                {getUniqueOptions('tags').flatMap(tag => 
                  ['Engineering', 'Management', 'Data', 'Leadership'].includes(tag) ? [tag] : []
                ).map(tag => (
                  <Select.Option key={tag} value={tag.toLowerCase()}>{tag}</Select.Option>
                ))}
              </Select>
            </Col>
            <Col xs={12} md={4}>
              <Select 
                size="large"
                value={selectedLocation}
                onChange={setSelectedLocation}
                style={{ width: '100%' }}
              >
                <Select.Option value="all">All Locations</Select.Option>
                {getUniqueOptions('location').map(location => (
                  <Select.Option key={location} value={location.toLowerCase()}>{location}</Select.Option>
                ))}
              </Select>
            </Col>
            <Col xs={12} md={4}>
              <Select 
                size="large"
                value={selectedType}
                onChange={setSelectedType}
                style={{ width: '100%' }}
              >
                <Select.Option value="all">All Types</Select.Option>
                {getUniqueOptions('type').map(type => (
                  <Select.Option key={type} value={type.toLowerCase()}>{type}</Select.Option>
                ))}
              </Select>
            </Col>
            <Col xs={12} md={4}>
              <Select 
                size="large"
                value={selectedSource}
                onChange={setSelectedSource}
                style={{ width: '100%' }}
              >
                <Select.Option value="all">All Sources</Select.Option>
                {getUniqueOptions('source').map(source => (
                  <Select.Option key={source} value={source.toLowerCase()}>{source}</Select.Option>
                ))}
              </Select>
            </Col>
          </Row>
        </Card>
        <Card style={{ borderRadius: '12px', boxShadow: '0 2px 8px rgba(0,0,0,0.06)' }}>
          <div style={{ marginBottom: '16px' }}>
            <Title level={4} style={{ margin: 0 }}>
              Remote Engineering Jobs ({jobs.length})
            </Title>
          </div>
          <Table
            columns={columns}
            dataSource={jobs}
            rowKey="id"
            loading={isRefreshing}
            pagination={{
              pageSize: 10,
              showSizeChanger: false,
              showQuickJumper: true,
              showTotal: (total, range) => `${range[0]}-${range[1]} of ${total} jobs`
            }}
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
  );
}

export default function AppWrapper() {
  return (
    <AuthProvider>
      {<App />}
    </AuthProvider>
  );
}