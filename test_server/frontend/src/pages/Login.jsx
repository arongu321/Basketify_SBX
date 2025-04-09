import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../utils/api';
import { ACCESS_TOKEN, REFRESH_TOKEN } from '../utils/constants';

// FR2 - Login component for authenticating users
/**
 * @returns {JSX.Element} - The Login component.
 * @description FR2 - Login component for authenticating users. Allows users to enter their email and password to log in.
 * Handles authentication by sending a POST request to the API.
 * If the email is not verified, it displays an option to resend the verification email.
 * Provides links to register, reset password, or change email.
 */
export default function Login() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [showResendVerification, setShowResendVerification] = useState(false);
    const [isResending, setIsResending] = useState(false);
    const [resendSuccess, setResendSuccess] = useState(false);

    const navigate = useNavigate();

    // FR2 - Resend verification email when email is not verified
    const handleResendVerification = async () => {
        setIsResending(true);
        try {
            await api.post('/accounts/verify-email/', { email });
            setResendSuccess(true);
            setTimeout(() => {
                setResendSuccess(false);
            }, 5000); // Hide success message after 5 seconds
        } catch (err) {
            setError('Failed to send verification email. Please try again.');
        } finally {
            setIsResending(false);
        }
    };

    // FR2 - Handle login form submission and store JWT token on success
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            const response = await api.post('/api/token/', {
                email,
                password,
            });
            const accessToken = response.data.access;
            const refreshToken = response.data.refresh;

            localStorage.setItem(ACCESS_TOKEN, accessToken);
            localStorage.setItem(REFRESH_TOKEN, refreshToken);

            navigate('/');
        } catch (err) {
            if (err.response && err.response.data) {
                // FR2 - Check for unverified email error
                if (err.response.data.code === 'email_not_verified') {
                    setError(err.response.data.detail);

                    // FR2 - Option to resend verification email when email not verified
                    setShowResendVerification(true);
                } else {
                    setError('Invalid email or password');
                }
            } else {
                setError('Invalid email or password');
            }
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-form-container">
            <h2>Login to Basketify</h2>
            {error && <div className="error-message">{error}</div>}
            {showResendVerification && (
                <div className="resend-verification-container">
                    <p>Need a new verification email?</p>
                    {resendSuccess ? (
                        <div className="success-message">
                            Verification email sent! Please check your inbox.
                        </div>
                    ) : (
                        <button
                            onClick={handleResendVerification}
                            className="resend-verification-button"
                            disabled={isResending}
                        >
                            {isResending
                                ? 'Sending...'
                                : 'Resend Verification Email'}
                        </button>
                    )}
                </div>
            )}
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
                <div className="form-group">
                    <label htmlFor="password">Password</label>
                    <input
                        type="password"
                        id="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                    />
                </div>
                <button
                    type="submit"
                    className="auth-button"
                    disabled={loading}
                >
                    {loading ? 'Logging in...' : 'Login'}
                </button>
            </form>
            <p>
                Don't have an account? <Link to="/register">Register here</Link>
            </p>
            {/* FR3 - Links to forgot password and email change pages */}
            <p>
                <Link to="/password-reset" className="forgot-password-link">
                    Forgot your password?
                </Link>
            </p>
            <p>
                <Link to="/email-reset" className="change-email-link">
                    Change email?
                </Link>
            </p>
        </div>
    );
}
