function RecipeCard({ recipe, onClick }) {
    const getDifficultyColor = (difficulty) => {
        switch (difficulty?.toLowerCase()) {
            case 'easy': return '#4CAF50';
            case 'medium': return '#FF9800';
            case 'hard': return '#F44336';
            default: return '#9E9E9E';
        }
    };

    // Food emoji based on recipe type/name
    const getFoodEmoji = (name) => {
        const lowerName = name.toLowerCase();
        if (lowerName.includes('chicken')) return '🍗';
        if (lowerName.includes('pasta') || lowerName.includes('spaghetti')) return '🍝';
        if (lowerName.includes('pizza')) return '🍕';
        if (lowerName.includes('salad')) return '🥗';
        if (lowerName.includes('soup')) return '🍲';
        if (lowerName.includes('cake') || lowerName.includes('dessert')) return '🍰';
        if (lowerName.includes('cookie')) return '🍪';
        if (lowerName.includes('bread')) return '🍞';
        if (lowerName.includes('fish') || lowerName.includes('salmon')) return '🐟';
        if (lowerName.includes('beef') || lowerName.includes('steak')) return '🥩';
        if (lowerName.includes('rice')) return '🍚';
        if (lowerName.includes('egg')) return '🍳';
        if (lowerName.includes('taco') || lowerName.includes('mexican')) return '🌮';
        if (lowerName.includes('burger')) return '🍔';
        if (lowerName.includes('sandwich')) return '🥪';
        return '🍽️';
    };

    return (
        <div className="recipe-card" onClick={() => onClick(recipe)}>
            <div className="recipe-image">
                <span className="recipe-image-placeholder">{getFoodEmoji(recipe.name)}</span>
            </div>

            <div className="recipe-content">
                <h3 className="recipe-name">{recipe.name}</h3>
                <p className="recipe-description">{recipe.description}</p>

                <div className="recipe-meta">
                    <span className="recipe-badge time">
                        ⏱️ {recipe.cooking_time} min
                    </span>
                    <span
                        className="recipe-badge difficulty"
                        style={{
                            background: `${getDifficultyColor(recipe.difficulty)}15`,
                            color: getDifficultyColor(recipe.difficulty)
                        }}
                    >
                        {recipe.difficulty}
                    </span>
                    {recipe.calories && (
                        <span className="recipe-badge calories">
                            🔥 {Math.round(recipe.calories)} cal
                        </span>
                    )}
                </div>

                <div className="recipe-footer">
                    <span className="recipe-score">
                        ⭐ {((recipe.similarity_score || 0) * 100).toFixed(0)}% match
                    </span>
                    <button className="btn btn-sm btn-outline">View Details</button>
                </div>
            </div>
        </div>
    );
}

export default RecipeCard;
