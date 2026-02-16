import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { mealPlanService, recipeService } from '../services/api';

function MealPlannerPage() {
    const [mealPlan, setMealPlan] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [weekOffset, setWeekOffset] = useState(0);

    const navigate = useNavigate();

    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const mealTypes = ['breakfast', 'lunch', 'dinner'];

    // Calculate week dates based on offset
    const getWeekDates = (offset = 0) => {
        const today = new Date();
        const monday = new Date(today);
        monday.setDate(today.getDate() - today.getDay() + 1 + (offset * 7));

        const sunday = new Date(monday);
        sunday.setDate(monday.getDate() + 6);

        return {
            start: monday.toISOString().split('T')[0],
            end: sunday.toISOString().split('T')[0],
            monday
        };
    };

    const loadMealPlan = async () => {
        setLoading(true);
        setError(null);

        try {
            const { start, end } = getWeekDates(weekOffset);

            // Create or get meal plan for this week
            const plan = await mealPlanService.createMealPlan(start, end);
            setMealPlan(plan);
        } catch (err) {
            console.error('Error loading meal plan:', err);
            setError('Failed to load meal plan. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadMealPlan();
    }, [weekOffset]);

    const handleRemoveMeal = async (itemId) => {
        if (!mealPlan) return;

        try {
            await mealPlanService.removeMeal(mealPlan.plan_id, itemId);
            // Refresh meal plan
            loadMealPlan();
        } catch (err) {
            console.error('Error removing meal:', err);
            alert('Failed to remove meal. Please try again.');
        }
    };

    const getMealForSlot = (day, mealType) => {
        if (!mealPlan?.meals) return null;
        return mealPlan.meals.find(
            meal => meal.day_of_week === day && meal.meal_type === mealType
        );
    };

    const formatWeekRange = () => {
        const { start, end } = getWeekDates(weekOffset);
        const startDate = new Date(start);
        const endDate = new Date(end);

        const options = { month: 'short', day: 'numeric' };
        return `${startDate.toLocaleDateString('en-US', options)} - ${endDate.toLocaleDateString('en-US', options)}`;
    };

    if (loading) {
        return (
            <div className="page">
                <div className="loading">
                    <div className="spinner"></div>
                    <span className="loading-text">Loading meal plan...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="page">
            <div className="container">
                <div className="meal-planner">
                    {/* Week Navigation */}
                    <div className="week-nav">
                        <button
                            className="btn btn-secondary"
                            onClick={() => setWeekOffset(prev => prev - 1)}
                        >
                            ← Previous Week
                        </button>
                        <div className="week-title">
                            📅 Week of {formatWeekRange()}
                            {weekOffset === 0 && <span style={{ color: 'var(--primary)', marginLeft: '8px' }}>(Current)</span>}
                        </div>
                        <button
                            className="btn btn-secondary"
                            onClick={() => setWeekOffset(prev => prev + 1)}
                        >
                            Next Week →
                        </button>
                    </div>

                    {error && (
                        <div className="alert alert-error">
                            <span>⚠️</span>
                            <span>{error}</span>
                        </div>
                    )}

                    {/* Calendar Grid */}
                    <div className="calendar-grid">
                        {/* Header Row */}
                        <div className="calendar-header calendar-header meal-type"></div>
                        {days.map(day => (
                            <div key={day} className="calendar-header">
                                {day.substring(0, 3)}
                            </div>
                        ))}

                        {/* Meal Rows */}
                        {mealTypes.map(mealType => (
                            <>
                                <div key={`${mealType}-label`} className="calendar-header meal-type" style={{ textTransform: 'capitalize' }}>
                                    {mealType === 'breakfast' && '🌅'}
                                    {mealType === 'lunch' && '☀️'}
                                    {mealType === 'dinner' && '🌙'}
                                    {' '}{mealType}
                                </div>
                                {days.map(day => {
                                    const meal = getMealForSlot(day, mealType);
                                    return (
                                        <div key={`${day}-${mealType}`} className={`calendar-cell ${meal ? '' : 'empty'}`}>
                                            {meal ? (
                                                <div className="meal-card-mini" style={{ position: 'relative' }}>
                                                    <div className="meal-card-mini-name">{meal.recipe_name}</div>
                                                    <div className="meal-card-mini-time">⏱️ {meal.cooking_time} min</div>
                                                    <button
                                                        className="meal-card-mini-remove"
                                                        onClick={() => handleRemoveMeal(meal.item_id)}
                                                        style={{
                                                            position: 'absolute',
                                                            top: '4px',
                                                            right: '4px',
                                                            width: '20px',
                                                            height: '20px',
                                                            borderRadius: '50%',
                                                            background: 'var(--error)',
                                                            color: 'white',
                                                            fontSize: '12px',
                                                            border: 'none',
                                                            cursor: 'pointer',
                                                            display: 'flex',
                                                            alignItems: 'center',
                                                            justifyContent: 'center'
                                                        }}
                                                    >
                                                        ✕
                                                    </button>
                                                </div>
                                            ) : (
                                                <button
                                                    className="add-meal-btn"
                                                    onClick={() => navigate('/')}
                                                    title="Search for recipes to add"
                                                >
                                                    +
                                                </button>
                                            )}
                                        </div>
                                    );
                                })}
                            </>
                        ))}
                    </div>

                    {/* Actions */}
                    <div style={{
                        marginTop: 'var(--space-xl)',
                        display: 'flex',
                        gap: 'var(--space-md)',
                        justifyContent: 'center'
                    }}>
                        <button
                            className="btn btn-primary"
                            onClick={() => navigate('/')}
                        >
                            🔍 Search Recipes
                        </button>
                        {mealPlan?.meals?.length > 0 && (
                            <button
                                className="btn btn-secondary"
                                onClick={() => navigate('/shopping')}
                            >
                                🛒 Generate Shopping List
                            </button>
                        )}
                    </div>

                    {/* Tips */}
                    {(!mealPlan?.meals || mealPlan.meals.length === 0) && (
                        <div className="empty-state" style={{ marginTop: 'var(--space-2xl)' }}>
                            <div className="empty-icon">📅</div>
                            <h3 className="empty-title">Your meal plan is empty</h3>
                            <p className="empty-description">
                                Search for recipes on the home page and add them to your meal plan!
                            </p>
                            <button
                                className="btn btn-primary"
                                onClick={() => navigate('/')}
                            >
                                Start Planning
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default MealPlannerPage;
