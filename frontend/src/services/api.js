import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const checkHealth = async () => {
  const res = await api.get('/health');
  return res.data;
};

export const fetchDashboardSummary = async () => {
  const res = await api.get('/dashboard/summary');
  return res.data;
};

export const triggerDemoMode = async () => {
  const res = await api.post('/demo-data');
  return res.data;
};

export const uploadCSVFile = async (file) => {
  const formData = new FormData();
  formData.append('file', file);
  const res = await api.post('/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return res.data;
};

export const fetchComponents = async (params = {}) => {
  const res = await api.get('/components', { params });
  return res.data;
};

export const fetchComponentDetail = async (componentId) => {
  const res = await api.get(`/components/${componentId}`);
  return res.data;
};

export const fetchLots = async () => {
  const res = await api.get('/lots');
  return res.data;
};

export const fetchLotDetail = async (lotId) => {
  const res = await api.get(`/lots/${lotId}`);
  return res.data;
};

export const fetchModelPerformance = async () => {
  const res = await api.get('/model/performance');
  return res.data;
};

export const fetchAnomalies = async () => {
  const res = await api.get('/detect-anomalies');
  return res.data;
};

export const fetchExplanations = async (componentId) => {
  const res = await api.get(`/explanations/${componentId}`);
  return res.data;
};

export const fetchSettings = async () => {
  const res = await api.get('/settings');
  return res.data;
};

export const updateSettings = async (settings) => {
  const res = await api.post('/settings', settings);
  return res.data;
};

export const getExportURL = () => `${API_BASE_URL}/export/results`;

export default api;
