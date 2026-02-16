import { useState } from 'react';

function SearchBar({ onSearch, loading }) {
    const [query, setQuery] = useState('');

    const handleSubmit = (e) => {
        e.preventDefault();
        if (query.trim()) {
            onSearch(query.trim());
        }
    };

    return (
        <div className="search-container">
            <form onSubmit={handleSubmit} className="search-wrapper">
                <div className="search-input-wrapper">
                    <svg className="search-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <circle cx="11" cy="11" r="8" />
                        <path d="m21 21-4.35-4.35" />
                    </svg>
                    <input
                        type="text"
                        className="search-input"
                        placeholder="Search for recipes (e.g., 'quick vegetarian pasta')"
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                    />
                </div>
                <button
                    type="submit"
                    className="btn btn-primary btn-lg search-btn"
                    disabled={loading || !query.trim()}
                >
                    {loading ? (
                        <>
                            <div className="spinner" style={{ width: '20px', height: '20px', borderWidth: '2px' }}></div>
                            Searching...
                        </>
                    ) : (
                        'Get Recommendations'
                    )}
                </button>
            </form>
        </div>
    );
}

export default SearchBar;
