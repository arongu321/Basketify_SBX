// src/components/EmailVerification.js
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../utils/api';

function EmailVerification() {
    const [loading, setLoading] = useState(false);
    const [verified, setVerified] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        // Check if user is already verified
        const checkVerification = async () => {
            try {
                const response = await api.get('/accounts/profile/');
                if (response.data.email_is_verified) {
                    setVerified(true);
                }
            } catch (err) {
                console.error('Error checking verification status:', err);
            }
        };

        checkVerification();
    }, []);

    const handleResendVerification = async () => {
        setLoading(true);
        try {
            await api.post('/accounts/verify-email/');
            setLoading(false);
            alert('Verification email has been sent to your email address');
        } catch (err) {
            setError('Failed to send verification email');
            setLoading(false);
        }
    };

    if (verified) {
        return (
            <div className="verification-container">
                <h2>Email Verified</h2>
                <p>Your email has been successfully verified.</p>
                <button onClick={() => navigate('/')}>Go to Dashboard</button>
            </div>
        );
    }

    return (
        <div className="verification-container">
            <h2>Verify Your Email</h2>
            <p>
                Please check your email inbox for a verification link. If you
                didn't receive an email, you can request another one.
            </p>

            {error && <div className="error-message">{error}</div>}

            <button onClick={handleResendVerification} disabled={loading}>
                {loading ? 'Sending...' : 'Resend Verification Email'}
            </button>
        </div>
    );
}

export default EmailVerification;
