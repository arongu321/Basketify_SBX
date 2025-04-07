import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/Auth.css';

export default function EmailResetComplete() {
    return (
        <div className="auth-form-container">
            <h2>Email Change Complete</h2>
            <div className="success-message">
                <p>Your email has been changed successfully.</p>
                <p>
                    A verification email has been sent to your new email
                    address. Please verify your new email to maintain full
                    access to your account.
                </p>
            </div>
            <Link to="/login" className="auth-button">
                Log In
            </Link>
        </div>
    );
}
