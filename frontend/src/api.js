import axios from 'axios';

const baseURL = import.meta.env.VITE_API_BASE_URL || '';
const api = axios.create({ baseURL });
let refreshPromise = null;
api.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) config.headers.Authorization = 'Bearer ' + token;
  return config;
});
api.interceptors.response.use(res => res, async error => {
  const original = error.config;
  if (error.response?.status === 401 && original && !original._retry &&
      !original.url.includes('/api/auth/login/') && !original.url.includes('/api/auth/register/')) {
    original._retry = true;
    try {
      if (!refreshPromise) {
        const refresh = localStorage.getItem('refresh_token');
        if (!refresh) throw new Error('No refresh token');
        refreshPromise = axios.post(baseURL + '/api/auth/token/refresh/', { refresh })
          .then(res => {
            localStorage.setItem('access_token', res.data.access);
            if (res.data.refresh) localStorage.setItem('refresh_token', res.data.refresh);
            return res.data.access;
          }).finally(() => { refreshPromise = null; });
      }
      const token = await refreshPromise;
      original.headers.Authorization = 'Bearer ' + token;
      return api(original);
    } catch {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      window.location.href = '/login';
    }
  }
  return Promise.reject(error);
});
export default api;
