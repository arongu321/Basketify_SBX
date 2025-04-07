import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Auth.css';

export default function EmailResetDone() {
    return (
        <div className="auth-form-container">
            <h2>Check Your Email</h2>
            <div className="success-message">
                <p>
                    We've sent you an email with instructions to change your
                    email address. Please check your inbox and follow the link
                    provided.
                </p>
                <p>
                    <strong>Important:</strong> The link in the email will
                    expire after 2 minutes.
                </p>
                <p>
                    If you don't receive an email within a few minutes, please
                    check your spam folder or make sure you entered the correct
                    email address.
                </p>
            </div>
            <div className="auth-links">
                <Link to="/login" className="auth-link">
                    Return to Login
                </Link>
            </div>
        </div>
    );
}
