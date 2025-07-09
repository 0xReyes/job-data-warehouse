import React, { useState, useEffect, useCallback } from 'react';
import { login as apiLogin, verifyAuth, fetchJobData, authenticatedFetch } from '../service/api';
import { AuthContext } from './AuthContext';


export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [authToken, setAuthToken] = useState(null);
  const [showLoginModal, setShowLoginModal] = useState(false);

  const handleAutoLogin = useCallback(async() => {
    if (loading) return;
    try {
      setLoading(true)
      const result = await apiLogin();
      if (result.success) {
        setAuthToken(result.token);
        setIsAuthenticated(true);
        localStorage.setItem('auth_token', result.token);
        console.log('Auto-login successful');
      } else {
        setTimeout(handleAutoLogin, 5000); // Retry every 5 seconds
      }
    } catch (error) {
      console.log(error);
      setTimeout(handleAutoLogin, 50000); // Retry every 5 seconds
    }
  }, [loading]);
  // Check if user is already authenticated on app load
  useEffect(() => {
    checkAuthStatus();
  }, [isAuthenticated]);

  // Show login modal if not authenticated and not loading
  useEffect(() => {
    if (!loading && !isAuthenticated) {
       handleAutoLogin();
    }
  }, [handleAutoLogin, loading, isAuthenticated]);


  const checkAuthStatus = async () => {
    try {
      // First, check if we have a stored token
      const isAuth = await verifyAuth();
      setIsAuthenticated(isAuth)
      return isAuth;
    } catch (error) {
      console.error('Auth check failed:', error);
      setIsAuthenticated(false);
      setAuthToken(null);
      localStorage.removeItem('auth_token');
    } finally {
      setLoading(false);
    }
  };

  const login = async () => {
    try {
      const result = await apiLogin();
      
      if (result.success) {
        setAuthToken(result.token);
        setIsAuthenticated(true);
        setShowLoginModal(false); // Hide modal on successful login
        // Store token in localStorage as fallback for axios interceptor
        localStorage.setItem('auth_token', result.token);
        return { success: true, message: result.message };
      } else {
        return { success: false, error: result.error };
      }
    } catch (error) {
      console.error('Login failed:', error);
      return { success: false, error: error.message };
    }
  };

  const logout = () => {
    setIsAuthenticated(false);
    setAuthToken(null);
    setShowLoginModal(true); // Show modal immediately after logout
    // Clear any stored tokens
    localStorage.removeItem('auth_token');
  };

  // Use the authenticatedFetch from API service
  const makeAuthenticatedRequest = async (url, options = {}) => {
    try {
      const response = await authenticatedFetch(url, options);
      
      // If we get 401, user session expired
      if (response.status === 401) {
        setIsAuthenticated(false);
        setAuthToken(null);
        localStorage.removeItem('auth_token');
        throw new Error('Session expired. Please login again.');
      }
      
      return response;
    } catch (error) {
      // Handle session expiry
      if (error.message.includes('Authentication required') || error.message.includes('session expired')) {
        setIsAuthenticated(false);
        setAuthToken(null);
        localStorage.removeItem('auth_token');
      }
      throw error;
    }
  };

  // Convenient method to fetch job data
  const getJobData = async () => {
    try {
      const result = await fetchJobData();
      return result;
    } catch (error) {
      // Handle auth errors
      if (error.message.includes('Authentication required')) {
        setIsAuthenticated(false);
        setAuthToken(null);
      }
      throw error;
    }
  };

  const value = {
    isAuthenticated,
    loading,
    login,
    logout,
    authenticatedFetch: makeAuthenticatedRequest,
    getJobData,
    authToken,
    showLoginModal,
    setShowLoginModal,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};