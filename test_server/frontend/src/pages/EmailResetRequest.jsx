import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../utils/api';
import '../styles/Auth.css';

export default function EmailResetRequest() {
    const [email, setEmail] = useState('');
    const [loading, setLoading] = useState(false);
    const [message, setMessage] = useState('');
    const [error, setError] = useState('');

    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');
        setMessage('');

        try {
            const response = await api.post('/accounts/email-change/', {
                email,
            });
            setMessage(response.data.message);
            setTimeout(() => {
                navigate('/email-reset-done');
            }, 2000);
        } catch (err) {
            if (
                err.response &&
                err.response.data &&
                err.response.data.message
            ) {
                setError(err.response.data.message);
            } else {
                setError(
                    'There was an error processing your request. Please try again.'
                );
            }
            console.error('Email reset error:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-form-container">
            <h2>Change Your Email</h2>
            <p>
                Enter your current email address and we'll send you a link to
                change your email.
            </p>

            {message && <div className="success-message">{message}</div>}
            {error && <div className="error-message">{error}</div>}

            <form onSubmit={handleSubmit} className="auth-form">
                <div className="form-group">
                    <label htmlFor="email">Current Email</label>
                    <input
                        type="email"
                        id="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                    />
                </div>
                <button
                    type="submit"
                    className="auth-button"
                    disabled={loading}
                >
                    {loading ? 'Processing...' : 'Continue'}
                </button>
            </form>
            <p>
                Remember your login details? <Link to="/login">Login here</Link>
            </p>
        </div>
    );
}
