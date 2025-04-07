import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/VerifyEmail.css';

export default function VerifyEmailComplete() {
    return (
        <div className="verify-email-container">
            <div className="alert alert-success">
                You have successfully verified your email
            </div>
            <p>You can now access all features of Basketify.</p>
            <Link to="/" className="home-link">
                Go to Dashboard
            </Link>
        </div>
    );
}
