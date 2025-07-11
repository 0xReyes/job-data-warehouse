import React, { useState, useEffect, useCallback, useContext } from 'react';
import {
  Button, Input, Tag, Table, Space, Typography, Card, Layout, Spin, message,
  ConfigProvider, theme as antdTheme, Tooltip, Drawer, Descriptions, Divider, App as AntApp,
} from 'antd';
import {
  EnvironmentOutlined, ClockCircleOutlined, LinkOutlined, EditOutlined,
  FileTextOutlined, GlobalOutlined,
} from '@ant-design/icons';

// Import your actual components here
// import AppHeader from './components/layout/AppHeader';
// import LoginPrompt from './components/auth/LoginPrompt';
// import CoverLetterModal from './components/jobs/CoverLetterModal';
// import JobTableSkeleton from './components/jobs/JobTableSkeleton';
// import EmptyState from './components/jobs/EmptyState';
// import JobSearch from './components/jobs/JobSearch'

// Import your actual AuthContext and AuthProvider
import { AuthContext } from './context/AuthContext';
import { AuthProvider } from './context/AuthProvider';

// Placeholder components - replace these with your actual component imports
const AppHeader = ({ onRefresh, isRefreshing }) => (
  <Layout.Header style={{ background: 'white', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
    <h1 style={{ margin: 0, color: '#4A90E2' }}>Job Tracker</h1>
    <Button onClick={onRefresh} loading={isRefreshing}>Refresh</Button>
  </Layout.Header>
);

const LoginPrompt = () => (
  <div style={{ textAlign: 'center', padding: '100px 0' }}>
    <h2>Please log in to continue</h2>
  </div>
);

const CoverLetterModal = ({ visible, onClose, job, onSave, initialData }) => (
  <div>{visible && <div>Cover Letter Modal for {job?.title}</div>}</div>
);

const JobTableSkeleton = () => (
  <div style={{ padding: '20px', textAlign: 'center' }}>
    <Spin size="large" />
    <p>Loading jobs...</p>
  </div>
);

const EmptyState = ({ search }) => (
  <div style={{ textAlign: 'center', padding: '40px' }}>
    <p>{search ? `No jobs found for "${search}"` : 'No jobs available'}</p>
  </div>
);

const JobSearch = ({ search, setSearch, resultsCount }) => (
  <div style={{ marginBottom: '16px' }}>
    <Input.Search
      placeholder="Search jobs by title, company, or location..."
      value={search}
      onChange={(e) => setSearch(e.target.value)}
      allowClear
      size="large"
    />
    <p style={{ margin: '8px 0 0 0', color: '#666' }}>
      {resultsCount} job{resultsCount !== 1 ? 's' : ''} found
    </p>
  </div>
);

const { Content } = Layout;
const { Title, Text, Paragraph } = Typography;

// Constants & Responsive Font Calculation
const STORAGE_KEYS = { JOB_DATA: 'jobTrackerData', APPLICATION_DATA: 'applicationData' };

const getResponsiveFontSize = () => {
  const { innerWidth: w, innerHeight: h } = window;
  const base = Math.max(10, Math.min(16, (w + h) / 140));
  return {
    base: `${base}px`,
    small: `${base - 2}px`,
    large: `${base + 2}px`,
    title: `${base + 4}px`
  };
};

// Inject responsive CSS with complete scrolling fixes
if (!document.querySelector('#job-tracker-styles')) {
  const updateStyles = () => {
    const font = getResponsiveFontSize();
    const existing = document.querySelector('#job-tracker-styles');
    if (existing) existing.remove();
    
    const style = document.createElement('style');
    style.id = 'job-tracker-styles';
    style.textContent = `
      /* Global resets and scroll foundation */
      * {
        box-sizing: border-box;
      }
      
      html {
        height: 100%;
        overflow-x: hidden;
        overscroll-behavior: none;
      }
      
      body {
        margin: 0;
        padding: 0;
        height: 100%;
        overflow-x: hidden;
        overscroll-behavior: none;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      }
      
      #root {
        height: 100%;
        overflow-x: hidden;
      }
      
      /* Main application layout fixes - ALLOW PAGE SCROLLING */
      .ant-layout {
        min-height: 100vh;
        overflow-x: hidden;
        overflow-y: auto;
      }
      
      .ant-layout-content {
        overflow-x: hidden;
        overflow-y: auto;
      }
      
      /* Prevent background bleed-through */
      .ant-layout-header {
        position: relative;
        z-index: 100;
        background: white !important;
        border-bottom: 1px solid #f0f0f0;
      }
      
      /* Container boundaries and scroll management - FLEXIBLE LAYOUT */
      .main-content-wrapper {
        padding: 8px;
        gap: 8px;
        background: #f7f9fc;
        min-height: calc(100vh - 64px); /* Ensure full height but allow overflow */
      }
      
      .search-container {
        background: white;
        border-radius: 8px;
        padding: 16px;
        margin-bottom: 8px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
      }
      
      .table-container {
        background: white;
        border-radius: 8px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin-bottom: 20px; /* Add space for pagination */
      }
      
      .table-container .ant-card {
        border: none;
        box-shadow: none;
      }
      
      .table-container .ant-card-body {
        padding: 0;
      }
      
      /* Table scrolling and layout fixes - LIMITED HEIGHT WITH INTERNAL SCROLL */
      .job-table .ant-table-container {
        overflow: auto !important;
        contain: layout style paint;
        max-height: 60vh; /* Limit table height to ensure pagination is visible */
      }
      
      .job-table .ant-table-header {
        position: sticky;
        top: 0;
        z-index: 15;
      }
      
      .job-table .ant-table-body {
        overflow: auto !important;
      }
      
      .job-table .ant-table-thead > tr > th {
        position: sticky !important;
        top: 0 !important;
        z-index: 15 !important;
        background: #fafafa !important;
        padding: 12px 8px !important;
        font-weight: 600;
        font-size: ${font.base} !important;
        white-space: nowrap;
        border-bottom: 2px solid #f0f0f0 !important;
      }
      
      .job-table .ant-table-tbody > tr > td {
        padding: 12px 8px !important;
        transition: background-color 0.2s;
        vertical-align: top;
        word-wrap: break-word;
        font-size: ${font.base} !important;
      }
      
      /* Pagination positioning - OUTSIDE SCROLL AREA */
      .job-table .ant-table-pagination {
        margin: 16px;
        text-align: center;
        position: relative;
        z-index: 5;
      }
      
      /* Typography sizing */
      .job-table * { font-size: ${font.base} !important; }
      .job-table .ant-typography h5 { 
        font-size: ${font.title} !important; 
        margin-bottom: 4px !important; 
      }
      
      /* Row styling */
      .table-row-hover:hover > td { 
        background: #f7f9fc !important; 
      }
      
      .table-row-with-notes { 
        position: relative; 
      }
      
      .table-row-with-notes > td:first-child::before { 
        content: ''; 
        position: absolute; 
        left: 4px; 
        top: 16px; 
        width: 4px; 
        height: 4px; 
        background: #4A90E2; 
        border-radius: 50%; 
      }
      
      /* Responsive text classes */
      .responsive-text { font-size: ${font.base} !important; }
      .responsive-small { font-size: ${font.small} !important; }
      .responsive-large { font-size: ${font.large} !important; }
      
      /* Loading state container */
      .loading-wrapper {
        height: 100vh;
        overflow: hidden;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-direction: column;
        background: #f7f9fc;
      }
      
      /* Modal and drawer z-index management */
      .ant-modal-wrap {
        z-index: 1000 !important;
      }
      
      .ant-drawer {
        z-index: 1000 !important;
      }
      
      .ant-drawer-content {
        overflow: auto;
        max-height: 100vh;
      }
      
      /* Expanded row styling */
      .ant-table-expanded-row > td {
        background: #fdfdfd !important;
        border-left: 2px solid #4A90E2 !important;
      }
      
      /* Scroll performance optimizations */
      .scroll-optimized {
        will-change: scroll-position;
        -webkit-overflow-scrolling: touch;
        overscroll-behavior: contain;
      }
      
      /* Mobile responsive adjustments */
      @media (max-width: 768px) {
        .main-content-wrapper {
          padding: 4px;
          gap: 4px;
        }
        
        .job-table .ant-table-container {
          max-height: 50vh; /* Smaller height on mobile */
        }
        
        .job-table .ant-table-thead > tr > th {
          padding: 8px 4px !important;
          font-size: ${font.small} !important;
        }
        
        .job-table .ant-table-tbody > tr > td {
          padding: 8px 4px !important;
          font-size: ${font.small} !important;
        }
      }
      
      /* Prevent iOS bounce scrolling issues */
      @supports (-webkit-touch-callout: none) {
        .table-container .ant-table-body {
          -webkit-overflow-scrolling: touch;
          overflow-scrolling: touch;
        }
      }
    `;
    document.head.appendChild(style);
  };
  
  updateStyles();
  window.addEventListener('resize', updateStyles);
}

const appTheme = {
  token: {
    colorPrimary: '#4A90E2',
    fontFamily: `-apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif`,
    fontSize: 14, 
    borderRadius: 8, 
    colorBgLayout: '#f7f9fc',
    colorText: '#333333', 
    colorTextSecondary: '#666666',
  },
  components: {
    Card: { 
      boxShadow: '0 4px 12px rgba(0,0,0,0.08)', 
      paddingLG: 24 
    },
    Table: { 
      headerBg: '#fafafa', 
      headerColor: '#333333' 
    },
    Button: { 
      primaryShadow: '0 2px 0 rgba(74, 144, 226, 0.1)' 
    },
    Modal: { 
      headerBg: '#ffffff' 
    },
  },
};

// Simple storage utility - no localStorage saving for job data
const storage = {
  save: (key, data) => {
    try {
      // Only save application data (notes), not job data
      if (key === STORAGE_KEYS.APPLICATION_DATA) {
        localStorage.setItem(key, JSON.stringify(data));
      }
      // Skip saving job data to localStorage
    } catch (e) { 
      console.error('Storage save error:', e); 
    }
  },
  get: (key, fallback = null) => {
    try { 
      return JSON.parse(localStorage.getItem(key)) || fallback; 
    } catch (e) { 
      console.error('Storage get error:', e); 
      return fallback; 
    }
  }
};

const extractDomain = (url) => {
  try { 
    return new URL(url).hostname.replace('www.', ''); 
  } catch { 
    return null; 
  }
};

const transformJobData = (rawData) => {
  // Handle the API response structure from your actual API
  let data;
  
  console.log('Raw data structure:', rawData); // Debug to see actual structure
  
  // If rawData has success property, extract the data
  if (rawData && rawData.success && rawData.data) {
    data = rawData.data;
  } 
  // If rawData is the direct data array (from authenticatedFetch returning Object.values)
  else if (Array.isArray(rawData)) {
    data = rawData;
  }
  // If rawData has data property
  else if (rawData && rawData.data) {
    data = rawData.data;
  }
  // If rawData is a plain object (could be the job data object)
  else if (rawData && typeof rawData === 'object') {
    // If it looks like a single job object, wrap in array
    if (rawData.title || rawData.job_title || rawData.company || rawData.company_name) {
      data = [rawData];
    } else {
      // Might be an object where values are job objects
      data = Object.values(rawData);
    }
  }
  // Fallback
  else {
    data = rawData;
  }
  
  if (!data || !Array.isArray(data)) {
    console.warn('Data is not an array:', data);
    return [];
  }
  
  const transform = (item, id) => {
    if (!item || typeof item !== 'object') {
      console.warn('Invalid job item:', item);
      return null;
    }
    
    return {
      id: item.link || item.id || item.url || `job-${id}`,
      title: item.title || item.job_title || item.position || 'Untitled Position',
      company: item.company_name || item.company || item.employer || 'Unknown Company',
      location: item.location || item.job_location || item.city || 'Location not specified',
      posted: item.date || item.date_posted || item.posted_date || item.created_at || 'Recently',
      source: extractDomain(item.link || item.url || item.source_url) || item.source || 'Direct',
      link: item.link || item.url || item.apply_url || '#',
      snippet: item.snippet || item.summary || (item.description ? item.description.substring(0, 200) + '...' : ''),
      description: item.description || item.job_description || item.details || '',
      employment_type: item.employment_type || item.job_type || item.type || 'FULL_TIME',
      job_location_type: item.job_location_type || item.remote_type || item.work_type || '',
      valid_through: item.valid_through || item.expiry_date || item.expires || '',
    };
  };

  return data
    .map((item, i) => transform(item, i))
    .filter(item => item !== null); // Remove any null items
};

function App() {
  const { isAuthenticated, loading, setLoading, getJobData } = useContext(AuthContext);
  const { token } = antdTheme.useToken();
  const { message: messageApi } = AntApp.useApp();
  
  const [jobs, setJobs] = useState([]);
  const [filteredJobs, setFilteredJobs] = useState([]);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [search, setSearch] = useState('');
  const [modalVisible, setModalVisible] = useState(false);
  const [selectedJob, setSelectedJob] = useState(null);
  const [applicationData, setApplicationData] = useState({});
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [drawerJob, setDrawerJob] = useState(null);
  const [hasLoadedOnce, setHasLoadedOnce] = useState(false);

  // Load & save application data
  useEffect(() => {
    setApplicationData(storage.get(STORAGE_KEYS.APPLICATION_DATA, {}));
  }, []);
  
  useEffect(() => {
    storage.save(STORAGE_KEYS.APPLICATION_DATA, applicationData);
  }, [applicationData]);

  const loadJobs = useCallback(async (forceRefresh = false) => {
    if (loading || (hasLoadedOnce && !forceRefresh)) return;

    if (setLoading) setLoading(true);
    setIsRefreshing(true);
    
    try {
      console.log('Fetching job data from API...');
      const rawData = await getJobData();
      console.log('API Response:', rawData);
      
      const transformedData = transformJobData(rawData);
      console.log('Transformed data count:', transformedData.length);
      console.log('Sample transformed job:', transformedData[0]);
      
      setJobs(transformedData);
      setFilteredJobs(transformedData);
      setHasLoadedOnce(true);
      
      if (transformedData.length > 0) {
        messageApi.success(`Loaded ${transformedData.length} job(s) from API`);
      } else {
        messageApi.warning('API returned data but no jobs were found after processing');
        console.warn('Raw data received but no jobs processed:', rawData);
      }
    } catch (error) {
      console.error('Error loading jobs:', error);
      messageApi.error(`Failed to load jobs: ${error.message}`);
      setJobs([]);
      setFilteredJobs([]);
    } finally {
      setIsRefreshing(false);
      if (setLoading) setLoading(false);
    }
  }, [getJobData, hasLoadedOnce, messageApi, loading, setLoading]);

  useEffect(() => {
    if (isAuthenticated && !hasLoadedOnce) {
      loadJobs();
    }
  }, [isAuthenticated, hasLoadedOnce, loadJobs]);

  // Search filter
  useEffect(() => {
    const term = search.toLowerCase().trim();
    setFilteredJobs(term ? jobs.filter(job =>
      ['title', 'company', 'location', 'snippet', 'description']
        .some(field => {
          const value = job[field];
          return value && typeof value === 'string' && value.toLowerCase().includes(term);
        })
    ) : jobs);
  }, [search, jobs]);

  const handlers = {
    editApp: useCallback(job => { 
      setSelectedJob(job); 
      setModalVisible(true); 
    }, []),
    viewDetails: useCallback(job => { 
      setDrawerJob(job); 
      setDrawerVisible(true); 
    }, []),
    saveApp: useCallback((jobId, data) => 
      setApplicationData(prev => ({ ...prev, [jobId]: data })), [])
  };

  // Responsive columns configuration
  const columns = [
    {
      title: 'Role', 
      key: 'role', 
      width: 300,
      render: (_, record) => (
        <div>
          <Title 
            level={5} 
            className="responsive-large" 
            style={{ 
              color: token.colorText, 
              fontWeight: 500,
              margin: 0,
              marginBottom: '4px'
            }}
          >
            {record.title}
          </Title>
          <Text 
            className="responsive-text" 
            style={{ 
              color: token.colorTextSecondary, 
              display: 'block' 
            }}
          >
            {record.company}
          </Text>
        </div>
      )
    },
    {
      title: 'Details', 
      key: 'details', 
      width: 250,
      render: (_, record) => (
        <Space direction="vertical" size={2}>
          <Text 
            className="responsive-text" 
            style={{ display: 'flex', alignItems: 'flex-start' }}
          >
            <EnvironmentOutlined 
              style={{ 
                color: token.colorTextSecondary, 
                marginRight: '4px', 
                marginTop: '2px', 
                flexShrink: 0 
              }} 
            /> 
            <span style={{ wordBreak: 'break-word' }}>
              {record.location}
            </span>
          </Text>
          <Text 
            className="responsive-small" 
            type="secondary" 
            style={{ display: 'flex', alignItems: 'center' }}
          >
            <ClockCircleOutlined 
              style={{ marginRight: '4px', flexShrink: 0 }} 
            /> 
            {record.posted}
          </Text>
          {record.employment_type !== 'FULL_TIME' && (
            <Tag size="small" color="blue" className="responsive-small">
              {record.employment_type.replace('_', ' ')}
            </Tag>
          )}
        </Space>
      )
    },
    {
      title: 'Source', 
      key: 'source', 
      responsive: ['md'], 
      width: 120,
      render: (_, record) => (
        <Tag icon={<GlobalOutlined/>} color="cyan" className="responsive-small">
          {record.source.length > 12 ? 
            record.source.substring(0, 12) + '...' : 
            record.source
          }
        </Tag>
      )
    },
    {
      title: 'Actions', 
      key: 'actions', 
      align: 'right', 
      width: 140,
      fixed: 'right',
      render: (_, record) => {
        const hasNotes = !!applicationData[record.id];
        return (
          <Space size="small" direction="vertical">
            <Button
              type="text" 
              size="small" 
              className="responsive-small"
              icon={hasNotes ? 
                <FileTextOutlined style={{color: token.colorPrimary}} /> : 
                <EditOutlined />
              }
              onClick={e => { 
                e.stopPropagation(); 
                handlers.editApp(record); 
              }}
              style={{ width: '100%', padding: '2px 8px' }}
            >
              {hasNotes ? 'Notes' : 'Add Notes'}
            </Button>
            <Button
              type="primary" 
              size="small" 
              className="responsive-small"
              icon={<LinkOutlined />}
              onClick={e => { 
                e.stopPropagation(); 
                window.open(record.link, '_blank'); 
              }}
              style={{ width: '100%', padding: '2px 8px' }}
            >
              Apply
            </Button>
          </Space>
        )
      }
    }
  ];

  if (!isAuthenticated) return (
    <ConfigProvider theme={appTheme}>
      <AntApp>
        <Layout>
          <AppHeader 
            onRefresh={() => loadJobs(true)} 
            isRefreshing={isRefreshing} 
          />
          <LoginPrompt />
        </Layout>
      </AntApp>
    </ConfigProvider>
  );

  if (loading && jobs.length === 0) return (
    <ConfigProvider theme={appTheme}>
      <AntApp>
        <Layout>
          <AppHeader 
            onRefresh={() => loadJobs(true)} 
            isRefreshing={isRefreshing} 
          />
          <div className="loading-wrapper">
            <Spin size="large" />
            <Title 
              level={5} 
              type="secondary" 
              style={{ marginTop: '20px' }}
            >
              Loading Application...
            </Title>
          </div>
        </Layout>
      </AntApp>
    </ConfigProvider>
  );

  return (
    <AntApp>
      <Layout>
      <AppHeader 
        onRefresh={() => loadJobs(true)} 
        isRefreshing={isRefreshing} 
      />
      
      <Content>
        <div className="main-content-wrapper">
          <div className="search-container">
            <JobSearch 
              search={search} 
              setSearch={setSearch} 
              resultsCount={filteredJobs.length} 
            />
          </div>
          
          <div className="table-container">
            <Card>
              {isRefreshing ? (
                <JobTableSkeleton columns={columns} />
              ) : (
                <Table
                  className="job-table scroll-optimized"
                  columns={columns}
                  dataSource={filteredJobs}
                  rowKey="id"
                  size="small"
                  scroll={{ 
                    x: 'max-content'
                  }}
                  sticky={{
                    offsetHeader: 0,
                  }}
                  pagination={{ 
                    pageSize: 20, 
                    showSizeChanger: true, 
                    showQuickJumper: true, 
                    position: ['bottomCenter'],
                    showTotal: (total, range) => 
                      `${range[0]}-${range[1]} of ${total} jobs`
                  }}
                  expandable={{
                    expandedRowRender: record => (
                      <div style={{ 
                        padding: '8px 12px', 
                        background: '#fdfdfd', 
                        borderLeft: `2px solid ${token.colorPrimary}` 
                      }}>
                        <Text 
                          className="responsive-small" 
                          style={{ 
                            whiteSpace: 'pre-wrap', 
                            wordBreak: 'break-word', 
                            color: token.colorTextSecondary 
                          }}
                        >
                          {record.snippet}
                        </Text>
                      </div>
                    ),
                    rowExpandable: record => !!record.snippet,
                  }}
                  onRow={record => ({ 
                    onClick: () => handlers.viewDetails(record), 
                    style: { cursor: 'pointer' } 
                  })}
                  rowClassName={record => 
                    `table-row-hover ${applicationData[record.id] ? 'table-row-with-notes' : ''}`
                  }
                  locale={{ 
                    emptyText: <EmptyState search={search} /> 
                  }}
                />
              )}
            </Card>
          </div>
        </div>

        {selectedJob && (
          <CoverLetterModal
            visible={modalVisible}
            onClose={() => setModalVisible(false)}
            job={selectedJob}
            onSave={handlers.saveApp}
            initialData={applicationData[selectedJob.id]}
          />
        )}

        {drawerJob && (
          <Drawer
            title="Job Details"
            placement="right"
            size="large"
            onClose={() => setDrawerVisible(false)}
            open={drawerVisible}
            extra={
              <Space>
                <Button 
                  icon={<EditOutlined />} 
                  onClick={() => { 
                    setDrawerVisible(false); 
                    handlers.editApp(drawerJob); 
                  }}
                >
                  Add Notes
                </Button>
                <Button 
                  type="primary" 
                  icon={<LinkOutlined />} 
                  onClick={() => window.open(drawerJob.link, '_blank')}
                >
                  Apply Now
                </Button>
              </Space>
            }
          >
            <div style={{ marginBottom: '24px' }}>
              <Title 
                level={3} 
                style={{ 
                  marginBottom: '8px', 
                  color: token.colorText 
                }}
              >
                {drawerJob.title}
              </Title>
              <Text 
                style={{ 
                  fontSize: '16px', 
                  color: token.colorTextSecondary 
                }}
              >
                {drawerJob.company}
              </Text>
            </div>

            <Descriptions bordered column={1} size="small">
              <Descriptions.Item label="Location">
                <Space>
                  <EnvironmentOutlined 
                    style={{ color: token.colorTextSecondary }} 
                  />
                  {drawerJob.location}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="Posted">
                <Space>
                  <ClockCircleOutlined 
                    style={{ color: token.colorTextSecondary }} 
                  />
                  {drawerJob.posted}
                </Space>
              </Descriptions.Item>
              <Descriptions.Item label="Employment Type">
                <Tag color="blue">
                  {drawerJob.employment_type?.replace('_', ' ')}
                </Tag>
              </Descriptions.Item>
              {drawerJob.job_location_type && (
                <Descriptions.Item label="Work Location">
                  <Tag color="green">
                    {drawerJob.job_location_type.replace('_', ' ')}
                  </Tag>
                </Descriptions.Item>
              )}
              <Descriptions.Item label="Source">
                <Space>
                  <GlobalOutlined 
                    style={{ color: token.colorTextSecondary }} 
                  />
                  <Tag icon={<GlobalOutlined />} color="cyan">
                    {drawerJob.source}
                  </Tag>
                </Space>
              </Descriptions.Item>
              {drawerJob.valid_through && drawerJob.valid_through !== 'N/A' && (
                <Descriptions.Item label="Valid Through">
                  {drawerJob.valid_through}
                </Descriptions.Item>
              )}
              <Descriptions.Item label="Application Link">
                <Button 
                  type="link" 
                  icon={<LinkOutlined />} 
                  onClick={() => window.open(drawerJob.link, '_blank')} 
                  style={{ padding: 0 }}
                >
                  Open Job Posting
                </Button>
              </Descriptions.Item>
            </Descriptions>

            {drawerJob.description && (
              <>
                <Divider orientation="left">Job Description</Divider>
                <Card 
                  size="small" 
                  style={{ 
                    backgroundColor: '#fafafa', 
                    border: '1px solid #f0f0f0', 
                    maxHeight: '400px', 
                    overflow: 'auto' 
                  }}
                >
                  <Paragraph 
                    style={{ whiteSpace: 'pre-wrap', margin: 0 }}
                  >
                    {drawerJob.description}
                  </Paragraph>
                </Card>
              </>
            )}

            {applicationData[drawerJob.id] && (
              <>
                <Divider orientation="left">Your Notes</Divider>
                <Card 
                  size="small" 
                  style={{ 
                    backgroundColor: '#f6f8fa', 
                    border: `1px solid ${token.colorPrimary}20` 
                  }}
                  extra={
                    <Button 
                      type="text" 
                      size="small" 
                      icon={<EditOutlined />} 
                      onClick={() => { 
                        setDrawerVisible(false); 
                        handlers.editApp(drawerJob); 
                      }}
                    >
                      Edit
                    </Button>
                  }
                >
                  <Text>{applicationData[drawerJob.id]}</Text>
                </Card>
              </>
            )}
          </Drawer>
        )}
      </Content>
    </Layout>
    </AntApp>
  );
}

export default function AppWrapper() {
  return (
    <ConfigProvider theme={appTheme}>
      <AntApp>
        <AuthProvider>
          <App />
        </AuthProvider>
      </AntApp>
    </ConfigProvider>
  );
}