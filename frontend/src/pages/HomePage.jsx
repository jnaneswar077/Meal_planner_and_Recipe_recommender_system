import { useState } from 'react';
import SearchBar from '../components/SearchBar';
import RecipeCard from '../components/RecipeCard';
import RecipeDetail from '../components/RecipeDetail';
import { recipeService } from '../services/api';

function HomePage() {
    const [recipes, setRecipes] = useState([]);
    const [selectedRecipe, setSelectedRecipe] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [hasSearched, setHasSearched] = useState(false);

    const handleSearch = async (query) => {
        setLoading(true);
        setError(null);
        setHasSearched(true);

        try {
            const data = await recipeService.getRecommendations(query);
            setRecipes(data.recommendations || []);
        } catch (err) {
            console.error('Search error:', err);
            setError(
                err.response?.status === 503
                    ? 'Recipe data is not available. Please ensure the backend is running with the correct data path.'
                    : 'Failed to get recommendations. Please try again.'
            );
            setRecipes([]);
        } finally {
            setLoading(false);
        }
    };

    const handleRecipeClick = (recipe) => {
        setSelectedRecipe(recipe);
    };

    const closeRecipeDetail = () => {
        setSelectedRecipe(null);
    };

    return (
        <div className="page">
            {/* Hero Section */}
            <section className="hero">
                <h1 className="hero-title">
                    Find Your Next <span>Favorite Meal</span>
                </h1>
                <p className="hero-subtitle">
                    AI-powered recipe recommendations tailored to your taste.
                    Search from 222,000+ recipes and discover something delicious.
                </p>
                <SearchBar onSearch={handleSearch} loading={loading} />
            </section>

            {/* Error Message */}
            {error && (
                <div className="container">
                    <div className="alert alert-error">
                        <span>⚠️</span>
                        <span>{error}</span>
                    </div>
                </div>
            )}

            {/* Loading State */}
            {loading && (
                <div className="loading">
                    <div className="spinner"></div>
                    <span className="loading-text">Finding the best recipes for you...</span>
                </div>
            )}

            {/* Recipe Results */}
            {!loading && recipes.length > 0 && (
                <section className="recipes-section container">
                    <h2 className="section-title">
                        🍽️ Recommended Recipes ({recipes.length})
                    </h2>
                    <div className="recipes-grid">
                        {recipes.map((recipe) => (
                            <RecipeCard
                                key={recipe.id}
                                recipe={recipe}
                                onClick={handleRecipeClick}
                            />
                        ))}
                    </div>
                </section>
            )}

            {/* Empty State */}
            {!loading && hasSearched && recipes.length === 0 && !error && (
                <div className="empty-state">
                    <div className="empty-icon">🔍</div>
                    <h3 className="empty-title">No recipes found</h3>
                    <p className="empty-description">
                        Try a different search term or adjust your filters
                    </p>
                </div>
            )}

            {/* Initial State */}
            {!loading && !hasSearched && (
                <section className="container" style={{ padding: 'var(--space-3xl) 0' }}>
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
                        gap: 'var(--space-xl)',
                        textAlign: 'center'
                    }}>
                        <div style={{ padding: 'var(--space-xl)' }}>
                            <div style={{ fontSize: '3rem', marginBottom: 'var(--space-md)' }}>🔍</div>
                            <h3 style={{ marginBottom: 'var(--space-sm)' }}>Smart Search</h3>
                            <p style={{ color: 'var(--text-secondary)' }}>
                                Use natural language to find recipes. Try "quick chicken dinner" or "healthy vegetarian lunch"
                            </p>
                        </div>
                        <div style={{ padding: 'var(--space-xl)' }}>
                            <div style={{ fontSize: '3rem', marginBottom: 'var(--space-md)' }}>📅</div>
                            <h3 style={{ marginBottom: 'var(--space-sm)' }}>Meal Planning</h3>
                            <p style={{ color: 'var(--text-secondary)' }}>
                                Add recipes to your weekly meal plan. Stay organized and eat well all week
                            </p>
                        </div>
                        <div style={{ padding: 'var(--space-xl)' }}>
                            <div style={{ fontSize: '3rem', marginBottom: 'var(--space-md)' }}>🛒</div>
                            <h3 style={{ marginBottom: 'var(--space-sm)' }}>Shopping Lists</h3>
                            <p style={{ color: 'var(--text-secondary)' }}>
                                Auto-generate shopping lists from your meal plan. Never forget an ingredient
                            </p>
                        </div>
                    </div>
                </section>
            )}

            {/* Recipe Detail Modal */}
            {selectedRecipe && (
                <RecipeDetail
                    recipe={selectedRecipe}
                    onClose={closeRecipeDetail}
                />
            )}
        </div>
    );
}

export default HomePage;
