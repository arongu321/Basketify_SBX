import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Link, useNavigate, Navigate } from 'react-router-dom';
import axios from 'axios';
import Login from './pages/Login';
import NotFound from './pages/NotFound';
import Register from './pages/Register';
import ProtectedRoute from './components/ProtectedRoute';
import SearchInterface from './components/SearchInterface';
import StatsPage from './components/StatsPage';
import StatsGraph from './components/StatsGraph';
import MLPredictions from './components/MLPredictions';
import logo from './assets/Basketify-Logo.png';
import './App.css';
import { ACCESS_TOKEN } from './utils/constants';

document.title = 'Basketify';
const favicon = document.querySelector("link[rel='icon']") || document.createElement('link');
favicon.rel = 'icon';
favicon.href = logo;
document.head.appendChild(favicon);

function Home({ message }) {
    const navigate = useNavigate();
    const [favorites, setFavorites] = useState({ player: null, team: null });

    useEffect(() => {
        // fetch user favorites
        axios.get('http://localhost:8000/accounts/get-favorite/', {
            headers: { Authorization: `Bearer ${localStorage.getItem(ACCESS_TOKEN)}` }
        })
        .then(response => {
            if (response.data) {
                setFavorites({
                    player: response.data.player || null,
                    team: response.data.team || null
                });
            }
        })
        .catch(error => {
            console.error("Error fetching user favorites:", error);
        });
    }, []);

    const dashboardTiles = [
        { title: 'Search Player/Team', path: '/search' },
        { title: 'ML Predictions', path: '/ml-predictions' },
        { 
            title: favorites.player ? `Favourite Player: ${favorites.player}` : 'Favourite Player', 
            path: favorites.player ? `/stats/player/${favorites.player}` : '/search',
            state: favorites.player ? null : { setFavorite: 'player' }
        },
        { 
            title: favorites.team ? `Favourite Team: ${favorites.team}` : 'Favourite Team', 
            path: favorites.team ? `/stats/team/${favorites.team}` : '/search',
            state: favorites.team ? null : { setFavorite: 'team' }
        },
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
                        onClick={() => navigate(tile.path, { state: tile.state })}
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
                            <ProtectedRoute>
                                <Home />
                            </ProtectedRoute>
                        }
                    />
                    <Route path="/login" element={<Login />} />
                    <Route path="/register" element={<Register />} />
                    <Route path="/logout" element={<Logout />} />
                    <Route path="*" element={<NotFound />} />
                    <Route path="/ml-predictions/" element={<MLPredictions />} />
                    <Route path="/search" element={<SearchInterface />} />
                    <Route path="/stats/:type/:name" element={<StatsPage />} />
                    <Route path="/stats-graph/:type/:name" element={<StatsGraph />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
