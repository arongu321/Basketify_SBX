import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../utils/api';

// FR1 - Registration component for creating new user accounts
/**
 * Renders the registration page, allowing users to create a new account.
 * Displays a form for email and password input, handles form submission,
 * and navigates the user to the login page upon successful registration.
 * Includes error handling and loading states for a smooth user experience.
 *
 * @returns {JSX.Element} The registration page component.
 */
export default function Register() {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const [registrationSuccess, setRegistrationSuccess] = useState(false);

    const navigate = useNavigate();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    // FR1 - Handle registration form submission
    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            // FR1 - Send registration data to backend
            await api.post('/api/register/', formData);
            setRegistrationSuccess(true); // Show success message instead of redirecting
        } catch (err) {
            setError(
                'Registration failed. Please check your information and try again.'
            );
            if (err.response && err.response.data) {
                console.error('Registration error:', err.response.data);
            } else {
                console.error('Registration error:', err);
            }
        } finally {
            setLoading(false);
        }
    };

    // Navigate to login page when button is clicked
    const goToLogin = () => {
        navigate('/login');
    };

    return (
        <div className="auth-form-container">
            <h2>Register for Basketify</h2>

            {registrationSuccess ? (
                // Show verification warning after successful registration
                <div className="registration-message">
                    <div className="success-message">
                        <p>
                            Registration successful! A verification email has
                            been sent to <strong>{formData.email}</strong>.
                        </p>
                    </div>

                    <div className="verification-warning">
                        <h3>⚠️ Important: 2-Minute Time Limit ⚠️</h3>
                        <p>
                            You must verify your email within{' '}
                            <strong>2 minutes</strong>, or your account will be
                            deleted automatically.
                        </p>
                        <p>
                            Please check your inbox (and spam folder)
                            immediately.
                        </p>
                    </div>

                    <button
                        onClick={goToLogin}
                        className="auth-button"
                        style={{ marginTop: '20px' }}
                    >
                        Go to Login Page
                    </button>
                </div>
            ) : (
                // FR1 - Registration form with email and password fields
                <>
                    {error && <div className="error-message">{error}</div>}
                    <form onSubmit={handleSubmit} className="auth-form">
                        <div className="form-group">
                            <label htmlFor="email">Email*</label>
                            <input
                                type="email"
                                id="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label htmlFor="password">Password*</label>
                            <input
                                type="password"
                                id="password"
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                required
                            />
                        </div>
                        <button
                            type="submit"
                            className="auth-button"
                            disabled={loading}
                        >
                            {loading ? 'Registering...' : 'Register'}
                        </button>
                    </form>
                    <p>
                        Already have an account? <a href="/login">Login here</a>
                    </p>
                </>
            )}
        </div>
    );
}
