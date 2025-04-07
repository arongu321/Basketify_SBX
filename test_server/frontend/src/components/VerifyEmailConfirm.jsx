import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../utils/api';
import './VerifyEmail.css';

export default function VerifyEmailConfirm() {
    const [message, setMessage] = useState('Verifying your email...');
    const [isSuccess, setIsSuccess] = useState(null);
    const { uidb64, token } = useParams();
    const navigate = useNavigate();

    // Enhanced error handling in useEffect
    useEffect(() => {
        const verifyEmail = async () => {
            try {
                const response = await api.get(
                    `/accounts/verify-email-confirm/${uidb64}/${token}/`
                );

                if (response.status === 200) {
                    setIsSuccess(true);
                    setMessage('Your email has been verified successfully!');

                    // Redirect to complete page after 2 seconds
                    setTimeout(() => {
                        navigate('/verify-email-complete');
                    }, 2000);
                } else {
                    setIsSuccess(false);
                    setMessage(
                        'The verification link is invalid or has expired.'
                    );
                }
            } catch (error) {
                setIsSuccess(false);
                console.error('Verification error:', error);

                // More detailed error reporting
                if (
                    error.response &&
                    error.response.data &&
                    error.response.data.message
                ) {
                    setMessage(error.response.data.message);
                } else {
                    setMessage(
                        'The verification link is invalid or has expired.'
                    );
                }
            }
        };

        verifyEmail();
    }, [uidb64, token, navigate]);

    return (
        <div className="verify-email-container">
            <div
                className={`alert ${
                    isSuccess === true
                        ? 'alert-success'
                        : isSuccess === false
                        ? 'alert-error'
                        : ''
                }`}
            >
                {message}
            </div>
            {isSuccess === false && (
                <div className="action-links">
                    <button
                        onClick={() => navigate('/verify-email')}
                        className="verify-btn"
                    >
                        Request New Verification Email
                    </button>
                </div>
            )}
        </div>
    );
}
