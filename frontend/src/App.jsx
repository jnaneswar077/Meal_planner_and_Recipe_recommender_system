import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useEffect, createContext } from 'react';
import Navbar from './components/Navbar';
import HomePage from './pages/HomePage';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import MealPlannerPage from './pages/MealPlannerPage';
import ShoppingPage from './pages/ShoppingPage';
import { authService } from './services/api';

// Auth Context
export const AuthContext = createContext(null);

// Protected Route Component
function ProtectedRoute({ children }) {
    const isAuth = authService.isAuthenticated();

    if (!isAuth) {
        return <Navigate to="/login" replace />;
    }

    return children;
}

function App() {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        // Check for existing auth
        const currentUser = authService.getCurrentUser();
        if (currentUser) {
            setUser(currentUser);
        }
        setLoading(false);
    }, []);

    const login = (userData) => {
        setUser(userData);
    };

    const logout = () => {
        authService.logout();
        setUser(null);
    };

    if (loading) {
        return (
            <div className="loading" style={{ height: '100vh' }}>
                <div className="spinner"></div>
                <span className="loading-text">Loading...</span>
            </div>
        );
    }

    return (
        <AuthContext.Provider value={{ user, login, logout }}>
            <Router>
                <div className="app">
                    <Navbar />
                    <main>
                        <Routes>
                            <Route path="/" element={<HomePage />} />
                            <Route path="/login" element={<LoginPage />} />
                            <Route path="/register" element={<RegisterPage />} />
                            <Route
                                path="/meal-planner"
                                element={
                                    <ProtectedRoute>
                                        <MealPlannerPage />
                                    </ProtectedRoute>
                                }
                            />
                            <Route
                                path="/shopping"
                                element={
                                    <ProtectedRoute>
                                        <ShoppingPage />
                                    </ProtectedRoute>
                                }
                            />
                            <Route path="*" element={<Navigate to="/" replace />} />
                        </Routes>
                    </main>
                </div>
            </Router>
        </AuthContext.Provider>
    );
}

export default App;
