import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../utils/api';
import '../styles/Auth.css';

export default function EmailResetConfirm() {
    const [newEmail, setNewEmail] = useState('');
    const [confirmNewEmail, setConfirmNewEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [validating, setValidating] = useState(true);
    const [tokenValid, setTokenValid] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');
    const [tokenExpired, setTokenExpired] = useState(false);

    const { uidb64, token } = useParams();
    const navigate = useNavigate();

    // Validate token when component mounts
    useEffect(() => {
        const validateToken = async () => {
            try {
                const response = await api.get(
                    `/accounts/email-change-confirm/${uidb64}/${token}/`
                );
                if (response.data.status === 'success') {
                    setTokenValid(true);
                } else {
                    setError(
                        'This email change link is invalid or has expired.'
                    );
                }
            } catch (err) {
                if (err.response && err.response.data) {
                    setError(
                        err.response.data.message ||
                            'This email change link is invalid or has expired.'
                    );
                    if (err.response.data.expired) {
                        setTokenExpired(true);
                    }
                } else {
                    setError(
                        'This email change link is invalid or has expired.'
                    );
                }
            } finally {
                setValidating(false);
            }
        };

        validateToken();
    }, [uidb64, token]);

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Basic validation
        if (newEmail !== confirmNewEmail) {
            setError('Email addresses do not match');
            return;
        }

        // Email format validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(newEmail)) {
            setError('Please enter a valid email address');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const response = await api.post(
                `/accounts/email-change-complete/${uidb64}/${token}/`,
                {
                    new_email: newEmail,
                }
            );

            if (response.data.status === 'success') {
                setMessage('Your email has been changed successfully!');
                setTimeout(() => {
                    navigate('/email-reset-complete');
                }, 2000);
            } else {
                setError('Failed to change email. Please try again.');
            }
        } catch (err) {
            if (err.response && err.response.data) {
                setError(
                    err.response.data.message ||
                        'There was an error changing your email. The link may have expired.'
                );
                if (err.response.data.expired) {
                    setTokenExpired(true);
                }
            } else {
                setError(
                    'There was an error changing your email. The link may have expired.'
                );
            }
        } finally {
            setLoading(false);
        }
    };

    if (validating) {
        return (
            <div className="auth-form-container">
                <h2>Change Your Email</h2>
                <p>Validating your email change link...</p>
            </div>
        );
    }

    if (!tokenValid || tokenExpired) {
        return (
            <div className="auth-form-container">
                <h2>Invalid or Expired Link</h2>
                <div className="error-message">
                    <p>{error}</p>
                    <p>Please request a new email change link.</p>
                </div>
                <button
                    className="auth-button"
                    onClick={() => navigate('/email-reset')}
                >
                    Request New Link
                </button>
            </div>
        );
    }

    return (
        <div className="auth-form-container">
            <h2>Change Your Email</h2>
            <p>Enter your new email address below.</p>

            {message && <div className="success-message">{message}</div>}
            {error && <div className="error-message">{error}</div>}

            <form onSubmit={handleSubmit} className="auth-form">
                <div className="form-group">
                    <label htmlFor="newEmail">New Email</label>
                    <input
                        type="email"
                        id="newEmail"
                        value={newEmail}
                        onChange={(e) => setNewEmail(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="confirmNewEmail">Confirm New Email</label>
                    <input
                        type="email"
                        id="confirmNewEmail"
                        value={confirmNewEmail}
                        onChange={(e) => setConfirmNewEmail(e.target.value)}
                        required
                    />
                </div>
                <button
                    type="submit"
                    className="auth-button"
                    disabled={loading}
                >
                    {loading ? 'Changing Email...' : 'Change Email'}
                </button>
            </form>
        </div>
    );
}
