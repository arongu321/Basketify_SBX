import axios from 'axios';
import { ACCESS_TOKEN } from './constants';

// Set a default baseURL
const apiURL = 'http://127.0.0.1:8000';

// Create an axios instance with a baseURL
const api = axios.create({
    baseURL: import.meta.env
        ? import.meta.env.REACT_APP_API_URL || apiURL
        : apiURL,
});

// Add an interceptor to include auth token in requests
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem(ACCESS_TOKEN);
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => {
        return Promise.reject(error);
    }
);

export default api;
