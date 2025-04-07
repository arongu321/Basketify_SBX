/*
Main dashboard of website to display search connection, favorites, and login connection.
Fulfills: FR4, FR5, FR6
*/

import React, { useEffect, useState } from 'react';
import {
    BrowserRouter as Router,
    Routes,
    Route,
    Link,
    useNavigate,
    Navigate,
} from 'react-router-dom';
import axios from 'axios';
import Login from './pages/Login';
import NotFound from './pages/NotFound';
import Register from './pages/Register';
import ProtectedRoute from './components/ProtectedRoute';
import SearchInterface from './components/SearchInterface';
import StatsPage from './components/StatsPage';
import StatsGraph from './components/StatsGraph';
import MLPredictions from './components/MLPredictions';
import EmailVerification from './components/EmailVerification';
import VerifyEmail from './components/VerifyEmail';
import VerifyEmailDone from './components/VerifyEmailDone';
import VerifyEmailConfirm from './components/VerifyEmailConfirm';
import VerifyEmailComplete from './components/VerifyEmailComplete';
import logo from './assets/Basketify-Logo.png';
import './App.css';
import { ACCESS_TOKEN } from './utils/constants';
import PasswordResetRequest from './pages/PasswordResetRequest';
import PasswordResetDone from './pages/PasswordResetDone';
import PasswordResetConfirm from './pages/PasswordResetConfirm';
import PasswordResetComplete from './pages/PasswordResetComplete';

document.title = 'Basketify';
const favicon =
    document.querySelector("link[rel='icon']") ||
    document.createElement('link');
favicon.rel = 'icon';
favicon.href = logo;
document.head.appendChild(favicon);

function Home({ message }) {
    const navigate = useNavigate();
    const [favorites, setFavorites] = useState({ player: null, team: null });
    const [loadingFavorites, setLoadingFavorites] = useState(true); // we only display dashboard when faves done loading

    useEffect(() => {
        // fetch user favorites and display if available: FR5, FR6
        axios
            .get('http://localhost:8000/accounts/get-favorite/', {
                headers: {
                    Authorization: `Bearer ${localStorage.getItem(
                        ACCESS_TOKEN
                    )}`,
                },
            })
            .then((response) => {
                if (response.data) {
                    setFavorites({
                        player: response.data.player || null,
                        team: response.data.team || null,
                    });
                }
                setLoadingFavorites(false); // done loading, display dashboard
            })
            .catch((error) => {
                console.error('Error fetching user favorites:', error);
                setLoadingFavorites(false);
            });
    }, []);

    // if faves still loading, show Basketify logo + msg
    if (loadingFavorites) {
        return (
            <div className="dashboard-loading-screen">
                <img
                    src={logo}
                    alt="Loading..."
                    className="dashboard-loading-favicon"
                />
                <h2>Loading...</h2>
            </div>
        );
    }

    const dashboardTiles = [
        { title: 'Search Player/Team', path: '/search' },  // connection to search page: FR4
        { title: 'ML Predictions', path: '/ml-predictions' },
        // connection to player favorite: FR6
        {
            title: favorites.player
                ? `Favourite Player: ${favorites.player}`
                : 'Favourite Player',
            path: favorites.player
                ? `/stats/player/${favorites.player}`
                : '/search',
            state: favorites.player ? null : { setFavorite: 'player' },
        },
        // connection to team favorite: FR5
        {
            title: favorites.team
                ? `Favourite Team: ${favorites.team}`
                : 'Favourite Team',
            path: favorites.team ? `/stats/team/${favorites.team}` : '/search',
            state: favorites.team ? null : { setFavorite: 'team' },
        },
    ];

    return (
        <div className="dashboard-container">
            <div className="dashboard-top-banner">
                <div className="dashboard-header-content">
                    <div className="dashboard-title-logo-container">
                        <img
                            src={logo}
                            alt="Basketify Logo"
                            className="dashboard-logo"
                        />
                        <h1 className="dashboard-title">Basketify</h1>
                    </div>
                    <Link to="/login" className="dashboard-login-link">
                        Login
                    </Link>
                </div>
            </div>

            <div className="dashboard-grid">
                {dashboardTiles.map((tile, index) => (
                    <div
                        key={index}
                        className="dashboard-tile"
                        onClick={() =>
                            navigate(tile.path, { state: tile.state })
                        }
                    >
                        <h2>{tile.title}</h2>
                    </div>
                ))}
            </div>

            <div className="dashboard-bottom-banner"></div>
        </div>
    );
}

function Logout() {
    localStorage.clear();
    return <Navigate to="/login" />;
}

function App() {
    const [message, setMessage] = useState('');

    useEffect(() => {
        axios.get('http://localhost:8000/api/load-database/');  // pre-fetch MongoDB connection
        axios
            .get('http://localhost:8000/api/')
            .then((response) => {
                setMessage(response.data.message);
            })
            .catch((error) => {
                console.log('There was an error!', error);
            });
    }, []);

    return (
        <Router>
            <div>
                <Routes>
                    <Route
                        path="/"
                        element={
                            <ProtectedRoute requireVerified={true}>
                                <Home />
                            </ProtectedRoute>
                        }
                    />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/logout" element={<Logout />} />

                    {/* Email verification routes */}
                    <Route path="/verify-email" element={<VerifyEmail />} />
                    <Route
                        path="/verify-email-done"
                        element={<VerifyEmailDone />}
                    />
                    <Route
                        path="/verify-email-confirm/:uidb64/:token"
                        element={<VerifyEmailConfirm />}
                    />
                    <Route
                        path="/verify-email-complete"
                        element={<VerifyEmailComplete />}
                    />

                    {/* Original EmailVerification component route (legacy) */}
                    <Route
                        path="/email-verification"
                        element={<EmailVerification />}
                    />

                    <Route
                        path="/password-reset"
                        element={<PasswordResetRequest />}
                    />
                    <Route
                        path="/password-reset-done"
                        element={<PasswordResetDone />}
                    />
                    <Route
                        path="/password-reset-confirm/:uidb64/:token"
                        element={<PasswordResetConfirm />}
                    />
                    <Route
                        path="/password-reset-complete"
                        element={<PasswordResetComplete />}
                    />

                    <Route path="*" element={<NotFound />} />
                    <Route
                        path="/ml-predictions/"
                        element={<MLPredictions />}
                    />
                    <Route path="/search" element={<SearchInterface />} />
                    <Route path="/stats/:type/:name" element={<StatsPage />} />
                    <Route
                        path="/stats-graph/:type/:name"
                        element={<StatsGraph />}
                    />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
