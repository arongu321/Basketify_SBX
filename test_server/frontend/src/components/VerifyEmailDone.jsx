import React from 'react';
import { Link } from 'react-router-dom';
import '../styles/VerifyEmail.css';

export default function VerifyEmailDone() {
    return (
        <div className="verify-email-container">
            <h3>
                An email has been sent with instructions to verify your email
            </h3>
            <p>
                Please check your inbox and click the verification link in the
                email. If you don't see the email, check your spam folder.
            </p>
            <Link to="/" className="home-link">
                Return to Dashboard
            </Link>
        </div>
    );
}
