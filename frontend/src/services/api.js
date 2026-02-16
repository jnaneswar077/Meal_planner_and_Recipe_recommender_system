/**
 * Smart Meal Planner - API Service
 * Handles all HTTP requests to the backend
 */

import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Add token to requests
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Handle auth errors
api.interceptors.response.use(
    (response) => response,
    (error) => {
        if (error.response?.status === 401) {
            localStorage.removeItem('token');
            localStorage.removeItem('user');
            window.location.href = '/login';
        }
        return Promise.reject(error);
    }
);

// ================================
// AUTH SERVICE
// ================================

export const authService = {
    register: async (userData) => {
        const response = await api.post('/auth/register', userData);
        if (response.data.token) {
            localStorage.setItem('token', response.data.token);
            localStorage.setItem('user', JSON.stringify({
                user_id: response.data.user_id,
                username: response.data.username
            }));
        }
        return response.data;
    },

    login: async (credentials) => {
        const response = await api.post('/auth/login', credentials);
        if (response.data.token) {
            localStorage.setItem('token', response.data.token);
            localStorage.setItem('user', JSON.stringify({
                user_id: response.data.user_id,
                username: response.data.username
            }));
        }
        return response.data;
    },

    logout: () => {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
    },

    getCurrentUser: () => {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    },

    isAuthenticated: () => {
        return !!localStorage.getItem('token');
    },

    getMe: async () => {
        const response = await api.get('/auth/me');
        return response.data;
    }
};

// ================================
// RECIPE SERVICE
// ================================

export const recipeService = {
    getRecommendations: async (query, filters = {}) => {
        const response = await api.post('/recipes/recommend', {
            query,
            n_recommendations: filters.n_recommendations || 6,
            dietary_restrictions: filters.dietary_restrictions,
            max_cooking_time: filters.max_cooking_time,
            difficulty: filters.difficulty,
            cuisine: filters.cuisine,
            meal_type: filters.meal_type
        });
        return response.data;
    },

    getRecipeDetail: async (recipeId) => {
        const response = await api.get(`/recipes/${recipeId}`);
        return response.data;
    },

    quickSearch: async (query, limit = 6) => {
        const response = await api.get('/recipes/search/quick', {
            params: { q: query, limit }
        });
        return response.data;
    }
};

// ================================
// MEAL PLAN SERVICE
// ================================

export const mealPlanService = {
    createMealPlan: async (weekStartDate, weekEndDate) => {
        const response = await api.post('/meal-plans/create', {
            week_start_date: weekStartDate,
            week_end_date: weekEndDate
        });
        return response.data;
    },

    getCurrentWeekPlan: async () => {
        const response = await api.get('/meal-plans/current');
        return response.data;
    },

    getMealPlan: async (planId) => {
        const response = await api.get(`/meal-plans/${planId}`);
        return response.data;
    },

    addMeal: async (planId, recipeId, dayOfWeek, mealType, date) => {
        const response = await api.post(`/meal-plans/${planId}/add-meal`, {
            recipe_id: recipeId,
            day_of_week: dayOfWeek,
            meal_type: mealType,
            date
        });
        return response.data;
    },

    removeMeal: async (planId, itemId) => {
        const response = await api.delete(`/meal-plans/${planId}/items/${itemId}`);
        return response.data;
    },

    listMealPlans: async () => {
        const response = await api.get('/meal-plans/');
        return response.data;
    }
};

// ================================
// SHOPPING SERVICE
// ================================

export const shoppingService = {
    generateList: async (planId) => {
        const response = await api.post('/shopping-lists/generate', {
            plan_id: planId
        });
        return response.data;
    },

    getShoppingList: async (listId) => {
        const response = await api.get(`/shopping-lists/${listId}`);
        return response.data;
    },

    toggleItem: async (listId, itemId, isChecked) => {
        const response = await api.patch(
            `/shopping-lists/${listId}/items/${itemId}`,
            { is_checked: isChecked }
        );
        return response.data;
    },

    deleteItem: async (listId, itemId) => {
        const response = await api.delete(`/shopping-lists/${listId}/items/${itemId}`);
        return response.data;
    },

    listShoppingLists: async () => {
        const response = await api.get('/shopping-lists/');
        return response.data;
    }
};

export default api;
