import React, { useState, useEffect } from 'react';
import { Navigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import api from '../utils/api';
import { ACCESS_TOKEN, REFRESH_TOKEN } from '../utils/constants';

export default function ProtectedRoute({ children }) {
    const [isAuthorized, setIsAuthorized] = useState(null);

    useEffect(() => {
        const checkAuth = async () => {
            const token = localStorage.getItem(ACCESS_TOKEN);

            if (!token) {
                setIsAuthorized(false);
                return;
            }

            try {
                // Check if token is expired
                const decoded = jwtDecode(token);
                const currentTime = Date.now() / 1000;

                if (decoded.exp < currentTime) {
                    // Token expired, try to refresh
                    const refreshToken = localStorage.getItem(REFRESH_TOKEN);

                    if (!refreshToken) {
                        setIsAuthorized(false);
                        return;
                    }

                    try {
                        const response = await api.post('/token/refresh/', {
                            refresh: refreshToken,
                        });

                        localStorage.setItem(
                            ACCESS_TOKEN,
                            response.data.access
                        );
                        setIsAuthorized(true);
                    } catch (err) {
                        localStorage.removeItem(ACCESS_TOKEN);
                        localStorage.removeItem(REFRESH_TOKEN);
                        setIsAuthorized(false);
                    }
                } else {
                    setIsAuthorized(true);
                }
            } catch (err) {
                console.error('Error decoding token:', err);
                setIsAuthorized(false);
            }
        };

        checkAuth();
    }, []);

    if (isAuthorized === null) {
        return <div>Loading...</div>;
    }

    return isAuthorized ? children : <Navigate to="/login" />;
}
