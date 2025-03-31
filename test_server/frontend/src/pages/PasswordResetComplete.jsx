import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Auth.css';

export default function PasswordResetComplete() {
    return (
        <div className="auth-form-container">
            <h2>Password Reset Complete</h2>
            <div className="success-message">
                <p>
                    Your password has been set. You can now log in with your new
                    password.
                </p>
            </div>
            <Link to="/login" className="auth-button">
                Log In
            </Link>
        </div>
    );
}
