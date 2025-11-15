/**
 * API Client for CantiereTrack Backend
 */
import axios, { AxiosInstance, AxiosError } from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle errors
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError) => {
    if (error.response?.status === 401) {
      // Unauthorized - clear token and redirect to login
      localStorage.removeItem('access_token');
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;

// Type definitions
export interface Employee {
  id: number;
  name: string;
  surname: string;
  badge_code: string;
  role: string;
  is_active: boolean;
  phone?: string;
  email?: string;
  created_at: string;
  updated_at: string;
}

export interface Site {
  id: number;
  name: string;
  address: string;
  city?: string;
  postal_code?: string;
  status: 'open' | 'closed';
  description?: string;
  created_at: string;
  updated_at: string;
}

export interface Attendance {
  id: number;
  employee_id: number;
  site_id: number;
  timestamp_in: string;
  timestamp_out?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
  employee?: {
    id: number;
    name: string;
    surname: string;
    badge_code: string;
    role: string;
  };
  site?: {
    id: number;
    name: string;
    address: string;
    status: string;
  };
}

export interface User {
  id: number;
  username: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  is_superuser: boolean;
  created_at: string;
  updated_at: string;
}

// API Functions

// Auth
export const login = async (username: string, password: string) => {
  const formData = new FormData();
  formData.append('username', username);
  formData.append('password', password);

  const response = await apiClient.post('/api/auth/login', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
};

export const register = async (userData: {
  username: string;
  email: string;
  password: string;
  full_name?: string;
}) => {
  const response = await apiClient.post('/api/auth/register', userData);
  return response.data;
};

// Employees
export const getEmployees = async (params?: {
  skip?: number;
  limit?: number;
  is_active?: boolean;
  search?: string;
}) => {
  const response = await apiClient.get('/api/employees/', { params });
  return response.data;
};

export const getEmployee = async (id: number) => {
  const response = await apiClient.get(`/api/employees/${id}`);
  return response.data;
};

export const createEmployee = async (data: {
  name: string;
  surname: string;
  badge_code: string;
  role: string;
  is_active?: boolean;
  phone?: string;
  email?: string;
}) => {
  const response = await apiClient.post('/api/employees/', data);
  return response.data;
};

export const updateEmployee = async (id: number, data: Partial<Employee>) => {
  const response = await apiClient.put(`/api/employees/${id}`, data);
  return response.data;
};

export const deleteEmployee = async (id: number) => {
  await apiClient.delete(`/api/employees/${id}`);
};

// Sites
export const getSites = async (params?: {
  skip?: number;
  limit?: number;
  status?: string;
  search?: string;
}) => {
  const response = await apiClient.get('/api/sites/', { params });
  return response.data;
};

export const getSite = async (id: number) => {
  const response = await apiClient.get(`/api/sites/${id}`);
  return response.data;
};

export const createSite = async (data: {
  name: string;
  address: string;
  city?: string;
  postal_code?: string;
  status?: 'open' | 'closed';
  description?: string;
}) => {
  const response = await apiClient.post('/api/sites/', data);
  return response.data;
};

export const updateSite = async (id: number, data: Partial<Site>) => {
  const response = await apiClient.put(`/api/sites/${id}`, data);
  return response.data;
};

export const deleteSite = async (id: number) => {
  await apiClient.delete(`/api/sites/${id}`);
};

// Attendance
export const getAttendances = async (params?: {
  skip?: number;
  limit?: number;
  employee_id?: number;
  site_id?: number;
  date_from?: string;
  date_to?: string;
}) => {
  const response = await apiClient.get('/api/attendance/', { params });
  return response.data;
};

export const getAttendance = async (id: number) => {
  const response = await apiClient.get(`/api/attendance/${id}`);
  return response.data;
};

export const clockIn = async (data: {
  employee_id: number;
  site_id: number;
  notes?: string;
}) => {
  const response = await apiClient.post('/api/attendance/clock-in', data);
  return response.data;
};

export const clockOut = async (attendanceId: number, notes?: string) => {
  const response = await apiClient.put(`/api/attendance/${attendanceId}/clock-out`, { notes });
  return response.data;
};

export const getActiveAttendance = async (employeeId: number) => {
  const response = await apiClient.get(`/api/attendance/employee/${employeeId}/active`);
  return response.data;
};

export const createAttendance = async (data: {
  employee_id: number;
  site_id: number;
  timestamp_in: string;
  timestamp_out?: string;
  notes?: string;
}) => {
  const response = await apiClient.post('/api/attendance/', data);
  return response.data;
};

export const updateAttendance = async (id: number, data: Partial<Attendance>) => {
  const response = await apiClient.put(`/api/attendance/${id}`, data);
  return response.data;
};

export const deleteAttendance = async (id: number) => {
  await apiClient.delete(`/api/attendance/${id}`);
};

// Reports
export const getEmployeeReport = async (
  employeeId: number,
  params?: {
    date_from?: string;
    date_to?: string;
  }
) => {
  const response = await apiClient.get(`/api/reports/employee/${employeeId}`, { params });
  return response.data;
};

export const getSiteReport = async (
  siteId: number,
  params?: {
    date_from?: string;
    date_to?: string;
  }
) => {
  const response = await apiClient.get(`/api/reports/site/${siteId}`, { params });
  return response.data;
};

export const downloadEmployeeReportCSV = async (
  employeeId: number,
  params?: {
    date_from?: string;
    date_to?: string;
  }
) => {
  const response = await apiClient.get(`/api/reports/employee/${employeeId}/csv`, {
    params,
    responseType: 'blob',
  });
  return response.data;
};

export const downloadSiteReportCSV = async (
  siteId: number,
  params?: {
    date_from?: string;
    date_to?: string;
  }
) => {
  const response = await apiClient.get(`/api/reports/site/${siteId}/csv`, {
    params,
    responseType: 'blob',
  });
  return response.data;
};
