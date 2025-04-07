import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';
import '../styles/VerifyEmail.css';

export default function VerifyEmail() {
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);

        try {
            await api.post('/accounts/verify-email/');
            navigate('/verify-email-done');
        } catch (error) {
            console.error('Error sending verification email:', error);
            setLoading(false);
        }
    };

    return (
        <div className="verify-email-container">
            <h1>You need to verify your email</h1>
            <form onSubmit={handleSubmit}>
                <button type="submit" className="verify-btn" disabled={loading}>
                    {loading ? 'Sending...' : 'Verify'}
                </button>
            </form>
        </div>
    );
}
