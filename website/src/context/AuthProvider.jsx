import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { login as apiLogin, verifyAuth, fetchJobData, authenticatedFetch } from '../service/api';
import { AuthContext } from './AuthContext';

export const AuthProvider = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(false);
  const [authToken, setAuthToken] = useState(null);
  const [showLoginModal, setShowLoginModal] = useState(false);

  // Auth status check and auto-login handler
  const checkAuthStatus = useCallback(async () => {
    if (loading) return;
    try {
      setLoading(true);
      const isAuth = await verifyAuth();
      setIsAuthenticated(isAuth);
      return isAuth;
    } catch (error) {
      console.error('Auth check failed:', error);
      localStorage.removeItem('auth_token');
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const handleAutoLogin = useCallback(async () => {
    if (loading) return;
    setLoading(true);
    try {
      if (await checkAuthStatus()){
        setIsAuthenticated(true);
      } else {
        setIsAuthenticated(true);
        const result = await apiLogin();
        if (result.success) {
          setAuthToken(result.token);
          setIsAuthenticated(true);
          localStorage.setItem('auth_token', result.token);
        }
      }
    } catch (error) {
      console.error('Auto-login error:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  // Trigger auto-login when not authenticated
  useEffect(() => {
    if (!loading && !isAuthenticated) {
      handleAutoLogin()
    }

  }, []);

  // Authentication methods
  const login = useCallback(async () => {
    if (loading) return;
    try {
      setLoading(true);
      const result = await apiLogin();
      
      if (result.success) {
        setAuthToken(result.token);
        response = await getJobData()
        if (response.success){
          setIsAuthenticated(true);
          setShowLoginModal(false);
          localStorage.setItem('auth_token', result.token);
          // localStorage.setItem('data', response.data);
        }
      }
      return result;
    } catch (error) {
      console.error('Login failed:', error);
      return { success: false, error: error.message };
    } finally {
      setLoading(false);
    }
  }, [isAuthenticated, loading]);

  const logout = useCallback(() => {
    setIsAuthenticated(false);
    setAuthToken(null);
    setShowLoginModal(true);
    localStorage.removeItem('auth_token');
    localStorage.removeItem('data');
  }, []);

  // API methods
  const makeAuthenticatedRequest = useCallback(async (url, options = {}) => {
    try {
      const response = await authenticatedFetch(url, options);
      if (response.status === 401) throw new Error('Session expired');
      return response;
    } catch (error) {
      if (error.message.includes('Authentication required') || error.message.includes('Session expired')) {
        logout();
      }
      throw error;
    }
  }, [logout]);

  const getJobData = useCallback(async () => {
    try {
      return await fetchJobData();
    } catch (error) {
      if (error.message.includes('Authentication required')) logout();
      throw error;
    }
  }, [logout]);

  // Memoized context value
  const contextValue = useMemo(() => ({
    isAuthenticated,
    loading,
    setLoading,
    authToken,
    showLoginModal,
    login,
    logout,
    setShowLoginModal,
    authenticatedFetch: makeAuthenticatedRequest,
    getJobData
  }), [
    isAuthenticated,
    loading,
    setLoading,
    authToken,
    showLoginModal,
    login,
    logout,
    makeAuthenticatedRequest,
    getJobData
  ]);

  return (
    <AuthContext.Provider value={contextValue}>
      {children}
    </AuthContext.Provider>
  );
};