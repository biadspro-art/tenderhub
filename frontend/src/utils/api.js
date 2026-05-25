import axios from 'axios';

const BASE = process.env.REACT_APP_API_URL || '';
const api = axios.create({ baseURL: BASE + '/api' });

api.interceptors.request.use(cfg => {
  const token = localStorage.getItem('token');
  if (token) cfg.headers.Authorization = `Bearer ${token}`;
  return cfg;
});

api.interceptors.response.use(
  r => r,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(err);
  }
);

export default api;

// Auth
export const login = (email, password) => {
  const form = new FormData();
  form.append('username', email);
  form.append('password', password);
  return api.post('/auth/login', form);
};
export const register = (data) => api.post('/auth/register', data);
export const getMe = () => api.get('/auth/me');

// Tenders
export const getTenders = (params) => api.get('/tenders', { params });

// Alerts
export const getAlerts = () => api.get('/alerts');
export const createAlert = (data) => api.post('/alerts', data);
export const updateAlert = (id, data) => api.put(`/alerts/${id}`, data);
export const toggleAlert = (id) => api.patch(`/alerts/${id}/toggle`);
export const deleteAlert = (id) => api.delete(`/alerts/${id}`);

// Saved Filters
export const getSavedFilters = () => api.get('/alerts/saved-filters');
export const createSavedFilter = (data) => api.post('/alerts/saved-filters', data);
export const deleteSavedFilter = (id) => api.delete(`/alerts/saved-filters/${id}`);

// Scraper
export const getSources = () => api.get('/scraper/sources');
export const triggerScrape = (data) => api.post('/scraper/trigger', data);
export const getScrapeLogs = () => api.get('/scraper/logs');
export const getDashboard = () => api.get('/scraper/dashboard');
