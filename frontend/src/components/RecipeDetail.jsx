import { useContext, useState } from 'react';
import { AuthContext } from '../App';
import { mealPlanService } from '../services/api';

function RecipeDetail({ recipe, onClose, onAddToMealPlan }) {
    const { user } = useContext(AuthContext);
    const [showMealSelector, setShowMealSelector] = useState(false);
    const [selectedDay, setSelectedDay] = useState('Monday');
    const [selectedMeal, setSelectedMeal] = useState('dinner');
    const [adding, setAdding] = useState(false);

    if (!recipe) return null;

    const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'];
    const mealTypes = ['breakfast', 'lunch', 'dinner'];

    const handleAddToMealPlan = async () => {
        if (!user) {
            alert('Please login to add recipes to your meal plan');
            return;
        }

        setAdding(true);
        try {
            // Get current week plan
            const plan = await mealPlanService.getCurrentWeekPlan();

            // Calculate date for selected day
            const today = new Date();
            const monday = new Date(today);
            monday.setDate(today.getDate() - today.getDay() + 1);

            const dayOffset = days.indexOf(selectedDay);
            const mealDate = new Date(monday);
            mealDate.setDate(monday.getDate() + dayOffset);

            const dateStr = mealDate.toISOString().split('T')[0];

            await mealPlanService.addMeal(
                plan.plan_id,
                recipe.id,
                selectedDay,
                selectedMeal,
                dateStr
            );

            alert(`Added "${recipe.name}" to ${selectedDay} ${selectedMeal}!`);
            setShowMealSelector(false);
            if (onAddToMealPlan) onAddToMealPlan();
        } catch (error) {
            console.error('Error adding to meal plan:', error);
            alert('Failed to add to meal plan. Please try again.');
        } finally {
            setAdding(false);
        }
    };

    return (
        <div className="modal-overlay" onClick={onClose}>
            <div className="modal-content" onClick={(e) => e.stopPropagation()}>
                <div className="modal-header">
                    <h2 className="modal-title">{recipe.name}</h2>
                    <button className="modal-close" onClick={onClose}>✕</button>
                </div>

                <div className="modal-body">
                    {/* Meta Info */}
                    <div className="recipe-meta" style={{ marginBottom: 'var(--space-xl)' }}>
                        <span className="recipe-badge time">⏱️ {recipe.cooking_time} min</span>
                        <span className="recipe-badge difficulty">{recipe.difficulty}</span>
                        <span className="recipe-badge">👨‍🍳 {recipe.n_steps} steps</span>
                        <span className="recipe-badge">🥕 {recipe.n_ingredients} ingredients</span>
                        {recipe.calories && (
                            <span className="recipe-badge calories">🔥 {Math.round(recipe.calories)} cal</span>
                        )}
                    </div>

                    {/* Tags */}
                    {(recipe.dietary_tags?.length > 0 || recipe.cuisine_tags?.length > 0) && (
                        <div className="detail-section">
                            <div style={{ display: 'flex', gap: 'var(--space-sm)', flexWrap: 'wrap' }}>
                                {recipe.dietary_tags?.map((tag, i) => (
                                    <span key={`diet-${i}`} className="recipe-badge" style={{ background: 'rgba(76, 175, 80, 0.1)', color: 'var(--primary)' }}>
                                        {tag}
                                    </span>
                                ))}
                                {recipe.cuisine_tags?.map((tag, i) => (
                                    <span key={`cuisine-${i}`} className="recipe-badge" style={{ background: 'rgba(255, 152, 0, 0.1)', color: 'var(--secondary-dark)' }}>
                                        {tag}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Description */}
                    <div className="detail-section">
                        <p style={{ color: 'var(--text-secondary)', lineHeight: '1.7' }}>
                            {recipe.description}
                        </p>
                    </div>

                    {/* Ingredients */}
                    <div className="detail-section">
                        <h3 className="detail-section-title">
                            <span>🥕</span> Ingredients
                        </h3>
                        <div className="ingredients-list">
                            {recipe.ingredients?.map((ingredient, index) => (
                                <div key={index} className="ingredient-item">
                                    <span className="ingredient-bullet"></span>
                                    <span>{ingredient}</span>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Steps */}
                    <div className="detail-section">
                        <h3 className="detail-section-title">
                            <span>📝</span> Instructions
                        </h3>
                        <div className="steps-list">
                            {recipe.steps?.map((step, index) => (
                                <div key={index} className="step-item">
                                    <span className="step-number">{index + 1}</span>
                                    <p className="step-text">{step}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Add to Meal Plan Section */}
                    {user && showMealSelector && (
                        <div className="detail-section" style={{
                            background: 'var(--bg-primary)',
                            padding: 'var(--space-lg)',
                            borderRadius: 'var(--radius-lg)'
                        }}>
                            <h4 style={{ marginBottom: 'var(--space-md)' }}>Add to Meal Plan</h4>
                            <div style={{ display: 'flex', gap: 'var(--space-md)', flexWrap: 'wrap', marginBottom: 'var(--space-lg)' }}>
                                <div className="form-group" style={{ flex: 1, minWidth: '150px', marginBottom: 0 }}>
                                    <label className="form-label">Day</label>
                                    <select
                                        className="form-input"
                                        value={selectedDay}
                                        onChange={(e) => setSelectedDay(e.target.value)}
                                    >
                                        {days.map(day => (
                                            <option key={day} value={day}>{day}</option>
                                        ))}
                                    </select>
                                </div>
                                <div className="form-group" style={{ flex: 1, minWidth: '150px', marginBottom: 0 }}>
                                    <label className="form-label">Meal</label>
                                    <select
                                        className="form-input"
                                        value={selectedMeal}
                                        onChange={(e) => setSelectedMeal(e.target.value)}
                                    >
                                        {mealTypes.map(meal => (
                                            <option key={meal} value={meal}>{meal.charAt(0).toUpperCase() + meal.slice(1)}</option>
                                        ))}
                                    </select>
                                </div>
                            </div>
                            <div style={{ display: 'flex', gap: 'var(--space-md)' }}>
                                <button
                                    className="btn btn-primary"
                                    onClick={handleAddToMealPlan}
                                    disabled={adding}
                                >
                                    {adding ? 'Adding...' : 'Add to Plan'}
                                </button>
                                <button
                                    className="btn btn-ghost"
                                    onClick={() => setShowMealSelector(false)}
                                >
                                    Cancel
                                </button>
                            </div>
                        </div>
                    )}
                </div>

                <div className="modal-footer">
                    {user && !showMealSelector && (
                        <button
                            className="btn btn-primary"
                            onClick={() => setShowMealSelector(true)}
                        >
                            ➕ Add to Meal Plan
                        </button>
                    )}
                    <button className="btn btn-secondary" onClick={onClose}>
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
}

export default RecipeDetail;
