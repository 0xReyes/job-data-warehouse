import React, { useState, useEffect } from 'react';
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
  FileTextOutlined
} from '@ant-design/icons';

const { Header, Content } = Layout;
const { Title, Text } = Typography;
const { TextArea } = Input;

const sampleApiData = {
  "organic": [
    {
      "title": "Claims Service Representative *Remote work*, anywhere in the GTA (Toronto, ON)",
      "link": "https://scm.wd3.myworkdayjobs.com/SCM/job/Toronto/Claims-Service-Representative--Remote-work---anywhere-in-the-GTA--Toronto--ON-_R0006396/apply",
      "snippet": "Start Your Application. Claims Service Representative *Remote work*, anywhere in the GTA (Toronto, ON). Autofill with Resume · Apply Manually.",
      "date": "21 hours ago",
      "position": 1
    },
    {
      "title": "Mobile Mortgage Specialist - TD Careers",
      "link": "https://td.wd3.myworkdayjobs.com/TD_Bank_Careers/job/Toronto-Ontario/Mobile-Mortgage-Specialist_R_1429632-1",
      "snippet": "Mobile Mortgage Specialist ; remote type: Remote ; locations: Toronto, Ontario ; time type: Full time ; posted on: Posted 4 Days Ago ; time left to apply: End Date: ...",
      "date": "16 hours ago",
      "position": 2
    },
    {
      "title": "(Remote) Senior Software Engineer",
      "link": "https://harriscomputer.wd3.myworkdayjobs.com/en-US/S_and_S/job/Illinois-United-States/XMLNAME--Remote--Senior-Software-Engineer_R0029565-8/apply",
      "snippet": "Senior Software Engineer (Billing and Accounting) Systems & Software - Remote Join Harris' Systems & Software, a pioneering force in the Utility CIS arena, ...",
      "date": "24 hours ago",
      "position": 3
    },
    {
      "title": "Telephone Banking Servicing Agent, Remote - Bilingual",
      "link": "https://cibc.wd3.myworkdayjobs.com/en-US/search/job/Montral-QC/Telephone-Banking-Servicing-Agent--Remote---Bilingual_2515091-1/apply/autofillWithResume",
      "snippet": "... remote work program and all employees may be given the opportunity to work from home, if you can meet the Agent@Home program requirements. Agent@Home ...",
      "date": "18 hours ago",
      "position": 4
    },
    {
      "title": "Remote Mutual Funds Representative - Contact Centre",
      "link": "https://cibc.wd3.myworkdayjobs.com/en-US/campus/job/Halifax-NS/Remote-Mutual-Funds-Representative---Contact-Centre-Investment-Team_2515546-1/apply/applyManually",
      "snippet": "... remote work program. All employees are required to meet the Agent@Home program requirements and be able to attend your primary work location within two ...",
      "date": "10 hours ago",
      "position": 5
    },
    {
      "title": "Senior Data Engineer (Toronto/ Montreal, Remote)",
      "link": "https://autodesk.wd1.myworkdayjobs.com/en-US/Ext/job/Montreal-QC-CAN/Senior-Data-Analyst--Toronto--Montreal--Remote-_25WD87271-2/apply/useMyLastApplication",
      "snippet": "Sign In. Search for Jobs. Back to Job Posting. Senior Data Engineer (Toronto/ Montreal, Remote). current step 1 of 6. step 2 of 6. step 3 of 6. step 4 of 6.",
      "date": "16 hours ago",
      "position": 7
    },
    {
      "title": "Head of Global Key Account Management EMEA (x|f|m)",
      "link": "https://sartorius.wd3.myworkdayjobs.com/en-US/sartoriuscareers/job/Home-Office-Germany/Head-of-Global-Key-Account-Management-EMEA---x-f-m----Remote_R36512-1/apply",
      "snippet": "Start Your Application. Head of Global Key Account Management EMEA (x|f|m) - Remote. Autofill with Resume · Apply Manually · Use My Last Application.",
      "date": "24 hours ago",
      "position": 8
    }
  ]
};

// Helper functions
const extractCompanyName = (link) => {
  if (link.includes('td.wd3.myworkdayjobs.com')) return 'TD Bank';
  if (link.includes('cibc.wd3.myworkdayjobs.com')) return 'CIBC';
  if (link.includes('autodesk.wd1.myworkdayjobs.com')) return 'Autodesk';
  if (link.includes('sartorius.wd3.myworkdayjobs.com')) return 'Sartorius';
  if (link.includes('harriscomputer.wd3.myworkdayjobs.com')) return 'Harris Computer';
  if (link.includes('scm.wd3.myworkdayjobs.com')) return 'SCM';
  return 'Company';
};

const extractTags = (title, snippet) => {
  const tags = [];
  if (title.toLowerCase().includes('senior') || title.toLowerCase().includes('sr')) tags.push('Senior');
  if (title.toLowerCase().includes('engineer')) tags.push('Engineering');
  if (title.toLowerCase().includes('manager')) tags.push('Management');
  if (title.toLowerCase().includes('specialist')) tags.push('Specialist');
  if (title.toLowerCase().includes('representative')) tags.push('Customer Service');
  if (title.toLowerCase().includes('data')) tags.push('Data');
  if (title.toLowerCase().includes('software')) tags.push('Software');
  if (title.toLowerCase().includes('mortgage')) tags.push('Finance');
  if (title.toLowerCase().includes('head of')) tags.push('Leadership');
  if (title.toLowerCase().includes('remote') || snippet.toLowerCase().includes('remote')) tags.push('Remote');
  return tags.slice(0, 3);
};

const extractLocation = (snippet) => {
  const locations = ['Toronto', 'Montreal', 'Halifax', 'Ontario', 'Quebec', 'Illinois', 'EMEA', 'Germany'];
  for (const location of locations) {
    if (snippet.includes(location)) return location;
  }
  return 'Remote';
};

const extractJobType = (snippet) => {
  if (snippet.toLowerCase().includes('full time') || snippet.toLowerCase().includes('full-time')) return 'Full-time';
  if (snippet.toLowerCase().includes('part time') || snippet.toLowerCase().includes('part-time')) return 'Part-time';
  if (snippet.toLowerCase().includes('contract')) return 'Contract';
  return 'Full-time';
};

const getJobBoardSource = (link) => {
  if (link.includes('myworkdayjobs.com')) return 'Workday';
  if (link.includes('greenhouse.io')) return 'Greenhouse';
  return 'Job Board';
};

const processApiJobs = (apiData) => {
  if (!apiData || !apiData.organic) return [];
  
  return apiData.organic.map((job, index) => ({
    id: `job-${index + 1}`,
    company: extractCompanyName(job.link),
    title: job.title,
    tags: extractTags(job.title, job.snippet),
    location: extractLocation(job.snippet),
    salary: 'Competitive',
    featured: index < 2,
    posted: job.date || 'Recently',
    type: extractJobType(job.snippet),
    description: job.snippet,
    link: job.link,
    source: getJobBoardSource(job.link),
    coverLetter: '',
    notes: ''
  }));
};

// Cover Letter Modal Component
const CoverLetterModal = ({ visible, onClose, job, onSave, initialData }) => {
  const [form] = Form.useForm();

  useEffect(() => {
    if (visible && initialData) {
      form.setFieldsValue(initialData);
    }
  }, [visible, initialData, form]);

  const handleSave = () => {
    form.validateFields().then(values => {
      onSave(job.id, values);
      onClose();
      message.success('Application notes saved!');
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
const AppHeader = ({ onRefresh, isLoading }) => (
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
        <Button 
          type="primary"
          ghost
          icon={<ReloadOutlined />} 
          onClick={onRefresh}
          loading={isLoading}
        >
          Refresh Jobs
        </Button>
      </Col>
    </Row>
  </Header>
);

// Main App Component
export default function App() {
  const [jobs, setJobs] = useState([]);
  const [allJobs, setAllJobs] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [search, setSearch] = useState('');
  const [selectedFunction, setSelectedFunction] = useState('all');
  const [selectedLocation, setSelectedLocation] = useState('all');
  const [selectedType, setSelectedType] = useState('all');
  const [selectedSource, setSelectedSource] = useState('all');
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [applicationData, setApplicationData] = useState({});

  // Get unique filter options from current jobs
  const getUniqueOptions = (key) => {
    const values = allJobs.map(job => job[key]).filter(Boolean);
    return [...new Set(values)].sort();
  };

  const fetchJobs = async () => {
    setIsLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 800));
      const processedJobs = processApiJobs(sampleApiData);
      setAllJobs(processedJobs);
      setJobs(processedJobs);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  useEffect(() => {
    let filtered = allJobs;

    if (search) {
      const searchTerm = search.toLowerCase();
      filtered = filtered.filter(job =>
        job.title.toLowerCase().includes(searchTerm) ||
        job.company.toLowerCase().includes(searchTerm) ||
        job.tags.some(tag => tag.toLowerCase().includes(searchTerm))
      );
    }

    if (selectedFunction !== 'all') {
      filtered = filtered.filter(job =>
        job.tags.some(tag => tag.toLowerCase().includes(selectedFunction.toLowerCase()))
      );
    }

    if (selectedLocation !== 'all') {
      filtered = filtered.filter(job =>
        job.location.toLowerCase().includes(selectedLocation.toLowerCase())
      );
    }

    if (selectedType !== 'all') {
      filtered = filtered.filter(job =>
        job.type.toLowerCase() === selectedType.toLowerCase()
      );
    }

    if (selectedSource !== 'all') {
      filtered = filtered.filter(job =>
        job.source.toLowerCase() === selectedSource.toLowerCase()
      );
    }

    setJobs(filtered);
  }, [allJobs, search, selectedFunction, selectedLocation, selectedType, selectedSource]);

  const handleEditApplication = (job) => {
    setSelectedJob(job);
    setModalVisible(true);
  };

  const handleSaveApplication = (jobId, data) => {
    setApplicationData(prev => ({
      ...prev,
      [jobId]: data
    }));
  };

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
            {record.tags.map(tag => (
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

  if (isLoading) {
    return (
      <Layout style={{ minHeight: '100vh', background: '#f0f2f5' }}>
        <AppHeader onRefresh={fetchJobs} isLoading={isLoading} />
        <Content style={{ padding: '48px', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
          <div style={{ textAlign: 'center' }}>
            <Spin size="large" />
            <div style={{ marginTop: '16px' }}>
              <Text type="secondary" style={{ fontSize: '16px' }}>Loading remote engineering jobs...</Text>
            </div>
          </div>
        </Content>
      </Layout>
    );
  }

  return (
    <Layout style={{ height: '100%', background: '#f0f2f5' }}>
      <AppHeader onRefresh={fetchJobs} isLoading={isLoading} />
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
            scroll={true}
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