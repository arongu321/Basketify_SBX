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

document.title = 'Basketify';
const favicon =
    document.querySelector("link[rel='icon']") ||
    document.createElement('link');
favicon.rel = 'icon';
favicon.href = logo;
document.head.appendChild(favicon);

function Home({ message }) {
    const navigate = useNavigate();

    const dashboardTiles = [
        { title: 'Search Player/Team', path: '/search' },
        { title: 'ML Predictions', path: '/ml-predictions' },
        { title: 'Favourite Player', path: '/stats/player/favorite' },
        { title: 'Favourite Team', path: '/stats/team/favorite' },
    ];

    return (
        <div className="dashboard-container">
            <div className="top-banner">
                <div className="header-content">
                    <div className="title-logo-container">
                        <img src={logo} alt="Basketify Logo" className="logo" />
                        <h1 className="title">Basketify</h1>
                    </div>
                    <Link to="/login" className="login-link">
                        Login
                    </Link>
                </div>
            </div>

            <div className="dashboard-grid">
                {dashboardTiles.map((tile, index) => (
                    <div
                        key={index}
                        className="dashboard-tile"
                        onClick={() => navigate(tile.path)}
                    >
                        <h2>{tile.title}</h2>
                    </div>
                ))}
            </div>

            <div className="bottom-banner"></div>
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
        axios.get('http://localhost:8000/api/load-database/');
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
