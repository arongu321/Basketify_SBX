import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../utils/api';
import '../styles/Auth.css';

export default function PasswordResetConfirm() {
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [validating, setValidating] = useState(true);
    const [tokenValid, setTokenValid] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const { uidb64, token } = useParams();
    const navigate = useNavigate();

    // Validate token when component mounts
    useEffect(() => {
        const validateToken = async () => {
            try {
                const response = await api.get(
                    `/accounts/password-reset-confirm/${uidb64}/${token}/`
                );
                if (response.data.status === 'success') {
                    setTokenValid(true);
                } else {
                    setError(
                        'This password reset link is invalid or has expired.'
                    );
                }
            } catch (err) {
                setError('This password reset link is invalid or has expired.');
            } finally {
                setValidating(false);
            }
        };

        validateToken();
    }, [uidb64, token]);

    const handleSubmit = async (e) => {
        e.preventDefault();

        // Basic validation
        if (password !== confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        if (password.length < 8) {
            setError('Password should be at least 8 characters long');
            return;
        }

        setLoading(true);
        setError('');

        try {
            const response = await api.post(
                `/accounts/password-reset-confirm/${uidb64}/${token}/`,
                {
                    password,
                }
            );

            if (response.data.status === 'success') {
                setMessage('Your password has been reset successfully!');
                setTimeout(() => {
                    navigate('/password-reset-complete');
                }, 2000);
            } else {
                setError('Failed to reset password. Please try again.');
            }
        } catch (err) {
            setError(
                'There was an error resetting your password. The link may have expired.'
            );
        } finally {
            setLoading(false);
        }
    };

    if (validating) {
        return (
            <div className="auth-form-container">
                <h2>Reset Your Password</h2>
                <p>Validating your reset link...</p>
            </div>
        );
    }

    if (!tokenValid) {
        return (
            <div className="auth-form-container">
                <h2>Invalid Reset Link</h2>
                <div className="error-message">
                    <p>{error}</p>
                    <p>Please request a new password reset link.</p>
                </div>
                <button
                    className="auth-button"
                    onClick={() => navigate('/password-reset')}
                >
                    Request New Reset Link
                </button>
            </div>
        );
    }

    return (
        <div className="auth-form-container">
            <h2>Set New Password</h2>

            {message && <div className="success-message">{message}</div>}
            {error && <div className="error-message">{error}</div>}

            <form onSubmit={handleSubmit} className="auth-form">
                <div className="form-group">
                    <label htmlFor="password">New Password</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <div className="form-group">
                    <label htmlFor="confirmPassword">Confirm Password</label>
                    <input
                        type="password"
                        id="confirmPassword"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        required
                    />
                </div>
                <button
                    type="submit"
                    className="auth-button"
                    disabled={loading}
                >
                    {loading ? 'Resetting Password...' : 'Reset Password'}
                </button>
            </form>
        </div>
    );
}
