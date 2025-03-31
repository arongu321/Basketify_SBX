import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../utils/api';
import '../styles/Auth.css';

export default function PasswordResetRequest() {
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
        console.log('Trying to reset password');

        try {
            const response = await api.post('/accounts/password-reset/', {
                email,
            });
            setMessage(response.data.message);
            setTimeout(() => {
                navigate('/password-reset-done');
            }, 2000);
        } catch (err) {
            setError(
                'There was an error processing your request. Please try again.'
            );
            console.error('Password reset error:', err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-form-container">
            <h2>Reset Your Password</h2>
            <p>
                Enter your email address and we'll send you a link to reset your
                password.
            </p>

            {message && <div className="success-message">{message}</div>}
            {error && <div className="error-message">{error}</div>}

            <form onSubmit={handleSubmit} className="auth-form">
                <div className="form-group">
                    <label htmlFor="email">Email</label>
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
                    {loading ? 'Processing...' : 'Reset Password'}
                </button>
            </form>
            <p>
                Remember your password? <Link to="/login">Login here</Link>
            </p>
        </div>
    );
}
