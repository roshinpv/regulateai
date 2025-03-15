import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { jwtDecode } from 'jwt-decode';
import { authAPI } from '../api';

interface User {
  id: string;
  username: string;
  email: string;
  is_admin: boolean;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (username: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

interface JWTPayload {
  exp: number;
  sub: string;
}

export const AuthProvider: React.FC<AuthProviderProps> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Check token expiry and validate it
  useEffect(() => {
    const validateToken = async () => {
      if (!token) {
        setIsLoading(false);
        return;
      }

      try {
        // Decode token and check expiry
        const decoded = jwtDecode<JWTPayload>(token);
        const currentTime = Date.now() / 1000;

        if (decoded.exp < currentTime) {
          // Token has expired
          console.log('Token expired, logging out');
          logout();
          return;
        }

        // For now, we'll just set mock user data
        // In a real app, you'd fetch this from the server
        setUser({
          id: 'user-001',
          username: decoded.sub,
          email: 'admin@example.com',
          is_admin: true,
          is_active: true
        });
      } catch (err) {
        console.error('Token validation error:', err);
        logout();
      } finally {
        setIsLoading(false);
      }
    };

    validateToken();

    // Set up token expiry check interval
    const checkTokenInterval = setInterval(() => {
      if (token) {
        try {
          const decoded = jwtDecode<JWTPayload>(token);
          const currentTime = Date.now() / 1000;
          
          if (decoded.exp < currentTime) {
            console.log('Token expired during interval check');
            logout();
          }
        } catch (err) {
          console.error('Token check error:', err);
          logout();
        }
      }
    }, 60000); // Check every minute

    return () => {
      clearInterval(checkTokenInterval);
    };
  }, [token]);

  const login = async (username: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      const data = await authAPI.login(username, password);
      localStorage.setItem('token', data.access_token);
      setToken(data.access_token);
      
      // Decode token to get expiry and username
      const decoded = jwtDecode<JWTPayload>(data.access_token);
      
      // Set user data
      setUser({
        id: 'user-001',
        username: decoded.sub,
        email: 'admin@example.com',
        is_admin: true,
        is_active: true
      });
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.response?.data?.detail || 'Login failed. Please check your credentials.');
      setToken(null);
      setUser(null);
      localStorage.removeItem('token');
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (username: string, email: string, password: string) => {
    setIsLoading(true);
    setError(null);
    
    try {
      await authAPI.register({ username, email, password });
      // After registration, log the user in
      await login(username, password);
    } catch (err: any) {
      console.error('Registration error:', err);
      setError(err.response?.data?.detail || 'Registration failed. Please try again.');
      setIsLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    setError(null);
  };

  const clearError = () => {
    setError(null);
  };

  const value = {
    user,
    token,
    isAuthenticated: !!user,
    isLoading,
    error,
    login,
    register,
    logout,
    clearError
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};