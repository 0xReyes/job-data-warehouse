// src/service/api.js
import axios from 'axios'

const API_BASE_URL = "https://github-utils-api.onrender.com";
const OWNER = "0xReyes";
const REPO = "ip-tools";

// Main API instance for GitHub operations
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Accept': 'application/vnd.github.v3+json',
  }
});

// Auth API instance for authentication operations
const authApi = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true, // Include cookies for authentication
  headers: {
    'Content-Type': 'application/json',
  }
});

// Authentication functions
export const login = async () => {
  try {
    const response = await authApi.post('/auth/login');
    
    if (response.status === 200) {
      return {
        success: true,
        token: response.data.token,
        message: response.data.message
      };
    } else {
      return {
        success: false,
        error: response.data.message || 'Authentication failed'
      };
    }
  } catch (error) {
    console.error('Login error:', error);
    return {
      success: false,
      error: error.response?.data?.message || error.message || 'Network error during login'
    };
  }
};

export const verifyAuth = async () => {
  try {
    const response = await authApi.get('/auth/verify');
    return response.status === 200 && response.data.success;
  } catch (error) {
    return false;
  }
};

export const logout = async () => {
  try {
    // Optional: call backend logout endpoint if you implement it
    await authApi.post('/auth/logout');
    return { success: true };
  } catch (error) {
    console.error('Logout error:', error);
    return { success: false, error: error.message };
  }
};

// Authenticated fetch function for protected resources
export const authenticatedFetch = async (url, options = {}) => {
  try {
    const fetchOptions = {
      ...options,
      credentials: 'include', // Include cookies
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    };

    const response = await authApi.get(url);
    if (response.status === 401) {
      throw new Error('Authentication required or session expired');
    }
    if (response.data){
      console.log(Object.values(response.data))
      return Object.values(response.data);
    }
    
  } catch (error) {
    console.error('Authenticated fetch error:', error);
    throw error;
  }
};

// Fetch job data with authentication
export const fetchJobData = async (options) => {
  try {
    const jobDataUrl = `${API_BASE_URL}/jobs`;
    const data = await authenticatedFetch(jobDataUrl);

    return {
      success: true,
      data
    };
  } catch (error) {
    console.error('Job data fetch error:', error);
    return {
      success: false,
      error: error.message
    };
  }
};

// Add request interceptor to include auth token if available
api.interceptors.request.use(
  (config) => {
    // Cookies are automatically included due to withCredentials: true
    // But you can also add Bearer token if needed
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Add response interceptor to handle auth errors for main API
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Handle auth failure
      localStorage.removeItem('auth_token');
      console.log('Authentication failed or expired');
    }
    return Promise.reject(error);
  }
);


export const getArtifacts = async () => {
  const url = `/api.github.com/repos/${OWNER}/${REPO}/actions/artifacts`;
  try {
    const response = await api.get(url);
    return response.data.artifacts.map(artifact => ({
      id: artifact.id,
      name: artifact.name,
      created: artifact.created_at,
      download_url: artifact.archive_download_url.replace('https://api.github.com', `${API_BASE_URL}/api.github.com`),
    }));
  } catch (error) {
    console.error("Error getting artifacts:", error.response?.data || error.message);
    throw new Error(`Failed to get artifacts: ${error.message}`);
  }
};

export const getArtifactByDispatchId = async (dispatchId) => {
  try {
    const artifacts = await getArtifacts();
    if (artifacts && artifacts.length > 0){
      console.log('getArtifactByDispatchId',dispatchId, artifacts)
      return artifacts.filter((artifact) => artifact.name.includes(dispatchId))
    } else {
      throw new Error(`Failed to fetch artifact`);
    }
  } catch (error) {
    console.error("Error getting artifact by ID:", error);
    throw new Error(`Failed to find artifact: ${error.message}`);
  }
};
