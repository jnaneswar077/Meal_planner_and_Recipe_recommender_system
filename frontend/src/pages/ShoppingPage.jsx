import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { shoppingService, mealPlanService } from '../services/api';

function ShoppingPage() {
    const [shoppingList, setShoppingList] = useState(null);
    const [mealPlan, setMealPlan] = useState(null);
    const [loading, setLoading] = useState(true);
    const [generating, setGenerating] = useState(false);
    const [error, setError] = useState(null);

    const navigate = useNavigate();

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            // Get current week's meal plan
            const plan = await mealPlanService.getCurrentWeekPlan();
            setMealPlan(plan);

            // Try to get existing shopping list
            const lists = await shoppingService.listShoppingLists();
            const currentList = lists.find(l => l.plan_id === plan.plan_id);
            if (currentList) {
                setShoppingList(currentList);
            }
        } catch (err) {
            console.error('Error loading data:', err);
            setError('Failed to load data. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateList = async () => {
        if (!mealPlan?.plan_id) return;

        setGenerating(true);
        setError(null);

        try {
            const list = await shoppingService.generateList(mealPlan.plan_id);
            setShoppingList(list);
        } catch (err) {
            console.error('Error generating list:', err);
            setError(err.response?.data?.detail || 'Failed to generate shopping list');
        } finally {
            setGenerating(false);
        }
    };

    const handleToggleItem = async (itemId, currentStatus) => {
        if (!shoppingList) return;

        try {
            await shoppingService.toggleItem(shoppingList.list_id, itemId, !currentStatus);
            // Update local state
            setShoppingList(prev => ({
                ...prev,
                items: prev.items.map(item =>
                    item.item_id === itemId
                        ? { ...item, is_checked: !currentStatus }
                        : item
                )
            }));
        } catch (err) {
            console.error('Error toggling item:', err);
        }
    };

    const handleDeleteItem = async (itemId) => {
        if (!shoppingList) return;

        try {
            await shoppingService.deleteItem(shoppingList.list_id, itemId);
            // Update local state
            setShoppingList(prev => ({
                ...prev,
                items: prev.items.filter(item => item.item_id !== itemId),
                total_items: prev.total_items - 1
            }));
        } catch (err) {
            console.error('Error deleting item:', err);
        }
    };

    const groupByCategory = (items) => {
        const groups = {};
        items?.forEach(item => {
            const category = item.category || 'other';
            if (!groups[category]) {
                groups[category] = [];
            }
            groups[category].push(item);
        });
        return groups;
    };

    const getCategoryEmoji = (category) => {
        const emojis = {
            vegetables: '🥬',
            fruits: '🍎',
            meat: '🥩',
            seafood: '🐟',
            dairy: '🧀',
            grains: '🌾',
            pantry: '🥫',
            herbs_spices: '🌿',
            other: '📦'
        };
        return emojis[category] || '📦';
    };

    const checkedCount = shoppingList?.items?.filter(i => i.is_checked).length || 0;
    const totalCount = shoppingList?.total_items || 0;

    if (loading) {
        return (
            <div className="page">
                <div className="loading">
                    <div className="spinner"></div>
                    <span className="loading-text">Loading shopping list...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="page">
            <div className="container">
                <div className="shopping-list">
                    {/* Header */}
                    <div className="shopping-header">
                        <div>
                            <h1 style={{ marginBottom: 'var(--space-xs)' }}>🛒 Shopping List</h1>
                            {shoppingList && (
                                <p style={{ color: 'var(--text-secondary)' }}>
                                    {checkedCount} of {totalCount} items checked
                                </p>
                            )}
                        </div>
                        <button
                            className="btn btn-primary"
                            onClick={handleGenerateList}
                            disabled={generating || !mealPlan?.meals?.length}
                        >
                            {generating ? 'Generating...' : '🔄 Generate from Meal Plan'}
                        </button>
                    </div>

                    {error && (
                        <div className="alert alert-error">
                            <span>⚠️</span>
                            <span>{error}</span>
                        </div>
                    )}

                    {/* Progress Bar */}
                    {shoppingList && totalCount > 0 && (
                        <div style={{
                            marginBottom: 'var(--space-xl)',
                            background: 'var(--bg-primary)',
                            borderRadius: 'var(--radius-full)',
                            height: '8px',
                            overflow: 'hidden'
                        }}>
                            <div style={{
                                width: `${(checkedCount / totalCount) * 100}%`,
                                height: '100%',
                                background: 'linear-gradient(90deg, var(--primary) 0%, var(--primary-light) 100%)',
                                transition: 'width var(--transition-base)'
                            }}></div>
                        </div>
                    )}

                    {/* Shopping List Items */}
                    {shoppingList && shoppingList.items?.length > 0 ? (
                        Object.entries(groupByCategory(shoppingList.items)).map(([category, items]) => (
                            <div key={category} className="shopping-category">
                                <h3 className="category-title">
                                    {getCategoryEmoji(category)} {category.replace('_', ' ')}
                                </h3>
                                {items.map(item => (
                                    <div
                                        key={item.item_id}
                                        className={`shopping-item ${item.is_checked ? 'checked' : ''}`}
                                    >
                                        <div
                                            className={`item-checkbox ${item.is_checked ? 'checked' : ''}`}
                                            onClick={() => handleToggleItem(item.item_id, item.is_checked)}
                                        >
                                            {item.is_checked && '✓'}
                                        </div>
                                        <span className="item-name">{item.ingredient_name}</span>
                                        <span className="item-quantity">
                                            {item.quantity > 1 ? `×${item.quantity}` : ''} {item.unit}
                                        </span>
                                        <button
                                            className="item-delete btn btn-ghost btn-sm"
                                            onClick={() => handleDeleteItem(item.item_id)}
                                        >
                                            🗑️
                                        </button>
                                    </div>
                                ))}
                            </div>
                        ))
                    ) : (
                        <div className="empty-state">
                            <div className="empty-icon">🛒</div>
                            <h3 className="empty-title">No shopping list yet</h3>
                            <p className="empty-description">
                                {mealPlan?.meals?.length > 0
                                    ? 'Click "Generate from Meal Plan" to create your shopping list'
                                    : 'Add some recipes to your meal plan first'}
                            </p>
                            {!mealPlan?.meals?.length && (
                                <button
                                    className="btn btn-primary"
                                    onClick={() => navigate('/meal-planner')}
                                >
                                    Go to Meal Planner
                                </button>
                            )}
                        </div>
                    )}

                    {/* Actions */}
                    {shoppingList && shoppingList.items?.length > 0 && (
                        <div style={{
                            marginTop: 'var(--space-xl)',
                            display: 'flex',
                            gap: 'var(--space-md)',
                            justifyContent: 'center'
                        }}>
                            <button
                                className="btn btn-secondary"
                                onClick={() => {
                                    shoppingList.items.forEach(item => {
                                        if (!item.is_checked) {
                                            handleToggleItem(item.item_id, false);
                                        }
                                    });
                                }}
                            >
                                ✓ Mark All as Bought
                            </button>
                            <button
                                className="btn btn-ghost"
                                onClick={() => {
                                    shoppingList.items.forEach(item => {
                                        if (item.is_checked) {
                                            handleToggleItem(item.item_id, true);
                                        }
                                    });
                                }}
                            >
                                Clear Checks
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}

export default ShoppingPage;
