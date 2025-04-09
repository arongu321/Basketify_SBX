import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter as Router } from 'react-router-dom';
import Register from '../pages/Register';
import Login from '../pages/Login';
import '@testing-library/jest-dom';
import api from '../utils/api';

// Mock the API calls
jest.mock('../utils/api');

describe('User Registration and Login Tests (FR1-FR3)', () => {
    afterEach(() => {
        jest.clearAllMocks();
    });

    // FR1 - User Registration Tests
    describe('FR1 - User Registration', () => {
        test('render_registration_form', () => {
            render(
                <Router>
                    <Register />
                </Router>
            );

            // Verify the registration form elements are visible
            expect(
                screen.getByText('Register for Basketify')
            ).toBeInTheDocument();
            expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
            expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
            expect(
                screen.getByRole('button', { name: /Register/i })
            ).toBeInTheDocument();
        });

        test('register_successful', async () => {
            // Mock successful API response
            api.post.mockResolvedValueOnce({
                data: { email: 'test@example.com' },
            });

            render(
                <Router>
                    <Register />
                </Router>
            );

            // Fill in the form
            fireEvent.change(screen.getByLabelText(/Email/i), {
                target: { value: 'test@example.com' },
            });
            fireEvent.change(screen.getByLabelText(/Password/i), {
                target: { value: 'password123' },
            });

            // Submit the form
            fireEvent.click(screen.getByRole('button', { name: /Register/i }));

            // Wait for the API call and success message
            await waitFor(() => {
                expect(api.post).toHaveBeenCalledWith('/api/register/', {
                    email: 'test@example.com',
                    password: 'password123',
                });
                expect(
                    screen.getByText(/Registration successful/i)
                ).toBeInTheDocument();
                expect(
                    screen.getByText(/2-Minute Time Limit/i)
                ).toBeInTheDocument(); // Verification warning
            });
        });

        test('register_error', async () => {
            // Mock API error response
            api.post.mockRejectedValueOnce({
                response: {
                    data: { email: ['A user with this email already exists.'] },
                },
            });

            render(
                <Router>
                    <Register />
                </Router>
            );

            // Fill in the form
            fireEvent.change(screen.getByLabelText(/Email/i), {
                target: { value: 'test@example.com' },
            });
            fireEvent.change(screen.getByLabelText(/Password/i), {
                target: { value: 'password123' },
            });

            // Submit the form
            fireEvent.click(screen.getByRole('button', { name: /Register/i }));

            // Wait for error message
            await waitFor(() => {
                expect(api.post).toHaveBeenCalled();
                expect(
                    screen.getByText(/Registration failed/i)
                ).toBeInTheDocument();
            });
        });
    });

    // FR2 - User Login Tests
    describe('FR2 - User Login', () => {
        test('render_login_form', () => {
            render(
                <Router>
                    <Login />
                </Router>
            );

            // Verify login form elements are visible
            expect(screen.getByLabelText(/Email/i)).toBeInTheDocument();
            expect(screen.getByLabelText(/Password/i)).toBeInTheDocument();
            expect(
                screen.getByRole('button', { name: /Login/i })
            ).toBeInTheDocument();
        });

        test('login_successful', async () => {
            // Mock successful login API response
            api.post.mockResolvedValueOnce({
                data: {
                    access: 'fake-access-token',
                    refresh: 'fake-refresh-token',
                },
            });

            render(
                <Router>
                    <Login />
                </Router>
            );

            // Fill in the form
            fireEvent.change(screen.getByLabelText(/Email/i), {
                target: { value: 'test@example.com' },
            });
            fireEvent.change(screen.getByLabelText(/Password/i), {
                target: { value: 'password123' },
            });

            // Submit the form
            fireEvent.click(screen.getByRole('button', { name: /Login/i }));

            // Check if API was called with correct data
            await waitFor(() => {
                expect(api.post).toHaveBeenCalledWith('/api/token/', {
                    email: 'test@example.com',
                    password: 'password123',
                });
            });
        });

        test('login_unverified_email', async () => {
            // Mock unverified email API response
            api.post.mockRejectedValueOnce({
                response: {
                    data: {
                        code: 'email_not_verified',
                        detail: 'Email not verified. Please check your inbox for the verification email.',
                    },
                },
            });

            render(
                <Router>
                    <Login />
                </Router>
            );

            // Fill in the form
            fireEvent.change(screen.getByLabelText(/Email/i), {
                target: { value: 'unverified@example.com' },
            });
            fireEvent.change(screen.getByLabelText(/Password/i), {
                target: { value: 'password123' },
            });

            // Submit the form
            fireEvent.click(screen.getByRole('button', { name: /Login/i }));

            // Check for error message and resend verification option
            await waitFor(() => {
                expect(api.post).toHaveBeenCalled();
                expect(
                    screen.getByText(/Need a new verification email/i)
                ).toBeInTheDocument();
                expect(
                    screen.getByRole('button', {
                        name: /Resend Verification Email/i,
                    })
                ).toBeInTheDocument();
            });
        });

        test('login_wrong_credentials', async () => {
            // Mock wrong credentials API response
            api.post.mockRejectedValueOnce({
                response: {},
            });

            render(
                <Router>
                    <Login />
                </Router>
            );

            // Fill in the form
            fireEvent.change(screen.getByLabelText(/Email/i), {
                target: { value: 'wrong@example.com' },
            });
            fireEvent.change(screen.getByLabelText(/Password/i), {
                target: { value: 'wrongpassword' },
            });

            // Submit the form
            fireEvent.click(screen.getByRole('button', { name: /Login/i }));

            // Check for error message
            await waitFor(() => {
                expect(api.post).toHaveBeenCalled();
                expect(
                    screen.getByText(/Invalid email or password/i)
                ).toBeInTheDocument();
            });
        });

        test('resend_verification_email', async () => {
            // First mock the login response for unverified email
            api.post.mockRejectedValueOnce({
                response: {
                    data: {
                        code: 'email_not_verified',
                        detail: 'Email not verified. Please check your inbox for the verification email.',
                    },
                },
            });

            // Then mock the resend verification response
            api.post.mockResolvedValueOnce({});

            render(
                <Router>
                    <Login />
                </Router>
            );

            // Fill in the form
            fireEvent.change(screen.getByLabelText(/Email/i), {
                target: { value: 'unverified@example.com' },
            });
            fireEvent.change(screen.getByLabelText(/Password/i), {
                target: { value: 'password123' },
            });

            // Submit the form
            fireEvent.click(screen.getByRole('button', { name: /Login/i }));

            // Wait for the resend button to appear
            await waitFor(() => {
                expect(
                    screen.getByRole('button', {
                        name: /Resend Verification Email/i,
                    })
                ).toBeInTheDocument();
            });

            // Click resend button
            fireEvent.click(
                screen.getByRole('button', {
                    name: /Resend Verification Email/i,
                })
            );

            // Verify resend API call
            await waitFor(() => {
                expect(api.post).toHaveBeenCalledWith(
                    '/accounts/verify-email/',
                    { email: 'unverified@example.com' }
                );
            });
        });
    });

    // FR3 - Password/Email Change Tests
    describe('FR3 - Password/Email Change', () => {
        test('render_password_reset_link', () => {
            render(
                <Router>
                    <Login />
                </Router>
            );

            // Verify password reset link is visible
            expect(
                screen.getByText(/Forgot your password/i)
            ).toBeInTheDocument();
        });

        test('render_email_change_link', () => {
            render(
                <Router>
                    <Login />
                </Router>
            );

            // Verify email change link is visible
            expect(screen.getByText(/Change email/i)).toBeInTheDocument();
        });
    });
});
