import React, { useState, useEffect } from 'react';
import { Link, useParams } from 'react-router-dom';
import axios from 'axios';

const BlogPage = () => {
  const [articles, setArticles] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [searchQuery, setSearchQuery] = useState('');

  const backendUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;

  useEffect(() => {
    loadArticles();
    loadCategories();
  }, [selectedCategory]);

  const loadArticles = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedCategory) params.append('category', selectedCategory);
      
      const response = await axios.get(`${backendUrl}/api/blog/articles?${params}`);
      if (response.data.success) {
        setArticles(response.data.articles);
      }
    } catch (error) {
      console.error('Erreur chargement articles:', error);
      // Articles par défaut en cas d'erreur
      setArticles([
        {
          id: '1',
          title: "Pourquoi l'eau du robinet peut être dangereuse pour votre santé",
          slug: "eau-robinet-dangereuse-sante",
          excerpt: "Découvrez les risques cachés de l'eau du robinet : chlore, métaux lourds, pesticides et micro-organismes qui menacent votre santé au quotidien.",
          category: "Santé",
          featured_image: "https://images.unsplash.com/photo-1548839140-29a749e1cf4d?w=800&h=400&fit=crop&q=80",
          published_date: "2024-09-19",
          reading_time: 8,
          view_count: 1250
        },
        {
          id: '2',
          title: "Les 7 bienfaits prouvés des osmoseurs pour votre famille",
          slug: "bienfaits-osmoseurs-famille",
          excerpt: "Découvrez comment l'osmose inverse transforme la santé de votre famille : meilleur goût, protection contre les contaminants, économies et bien-être.",
          category: "Bienfaits",
          featured_image: "https://images.unsplash.com/photo-1559827260-dc66d52bef19?w=800&h=400&fit=crop&q=80",
          published_date: "2024-09-18",
          reading_time: 12,
          view_count: 950
        },
        {
          id: '3',
          title: "Témoignages clients : Comment l'osmose inverse a changé leur vie",
          slug: "temoignages-clients-osmose-inverse",
          excerpt: "Découvrez les témoignages authentiques de nos clients qui ont transformé leur quotidien grâce aux osmoseurs Josmoze. Histoires vraies, résultats concrets.",
          category: "Témoignages",
          featured_image: "https://images.unsplash.com/photo-1600880292203-757bb62b4baf?w=800&h=400&fit=crop&q=80",
          published_date: "2024-09-17",
          reading_time: 15,
          view_count: 1890
        }
      ]);
    }
    setLoading(false);
  };

  const loadCategories = async () => {
    try {
      const response = await axios.get(`${backendUrl}/api/blog/categories`);
      if (response.data.success) {
        setCategories(response.data.categories);
      }
    } catch (error) {
      console.error('Erreur chargement catégories:', error);
      setCategories([
        { name: 'Santé', count: 5 },
        { name: 'Bienfaits', count: 3 },
        { name: 'Témoignages', count: 8 },
        { name: 'Conseils', count: 4 }
      ]);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) {
      loadArticles();
      return;
    }

    setLoading(true);
    try {
      const response = await axios.get(`${backendUrl}/api/blog/search?q=${encodeURIComponent(searchQuery)}`);
      if (response.data.success) {
        setArticles(response.data.results);
      }
    } catch (error) {
      console.error('Erreur recherche:', error);
    }
    setLoading(false);
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getCategoryColor = (category) => {
    const colors = {
      'Santé': 'bg-red-100 text-red-800',
      'Bienfaits': 'bg-green-100 text-green-800',
      'Témoignages': 'bg-blue-100 text-blue-800',
      'Conseils': 'bg-yellow-100 text-yellow-800'
    };
    return colors[category] || 'bg-gray-100 text-gray-800';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 text-white py-16">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">
              📚 Blog Josmoze
            </h1>
            <p className="text-xl md:text-2xl text-blue-100 mb-8">
              Tout savoir sur l'eau pure et l'osmose inverse
            </p>
            
            {/* Barre de recherche */}
            <div className="max-w-2xl mx-auto">
              <div className="flex rounded-lg overflow-hidden bg-white">
                <input
                  type="text"
                  placeholder="Rechercher un article..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
                  className="flex-1 px-6 py-4 text-gray-900 placeholder-gray-500 focus:outline-none"
                />
                <button
                  onClick={handleSearch}
                  className="px-8 py-4 bg-blue-600 text-white font-semibold hover:bg-blue-700 transition-colors"
                >
                  🔍 Rechercher
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-16">
        <div className="grid lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-lg p-6 sticky top-8">
              <h3 className="text-xl font-semibold text-gray-900 mb-4">
                📂 Catégories
              </h3>
              
              <div className="space-y-2">
                <button
                  onClick={() => {
                    setSelectedCategory('');
                    setSearchQuery('');
                  }}
                  className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                    selectedCategory === '' 
                      ? 'bg-blue-100 text-blue-800 font-semibold'
                      : 'hover:bg-gray-100'
                  }`}
                >
                  📄 Tous les articles
                </button>
                
                {categories.map((category) => (
                  <button
                    key={category.name}
                    onClick={() => {
                      setSelectedCategory(category.name);
                      setSearchQuery('');
                    }}
                    className={`w-full text-left px-4 py-2 rounded-lg transition-colors flex justify-between items-center ${
                      selectedCategory === category.name
                        ? 'bg-blue-100 text-blue-800 font-semibold'
                        : 'hover:bg-gray-100'
                    }`}
                  >
                    <span>{category.name}</span>
                    <span className="text-sm bg-gray-200 text-gray-600 px-2 py-1 rounded-full">
                      {category.count}
                    </span>
                  </button>
                ))}
              </div>

              {/* CTA */}
              <div className="mt-8 p-4 bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg">
                <h4 className="font-semibold text-gray-900 mb-2">
                  💧 Analysez votre eau
                </h4>
                <p className="text-sm text-gray-600 mb-4">
                  Test gratuit de la qualité de votre eau du robinet
                </p>
                <Link
                  to="/contact"
                  className="block w-full text-center bg-blue-600 text-white py-2 px-4 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                >
                  Test gratuit
                </Link>
              </div>
            </div>
          </div>

          {/* Articles Grid */}
          <div className="lg:col-span-3">
            {loading ? (
              <div className="text-center py-12">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
                <p className="text-gray-600">Chargement des articles...</p>
              </div>
            ) : articles.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">📝</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                  Aucun article trouvé
                </h3>
                <p className="text-gray-600">
                  {searchQuery 
                    ? `Aucun résultat pour "${searchQuery}"`
                    : 'Aucun article dans cette catégorie'
                  }
                </p>
              </div>
            ) : (
              <div className="grid md:grid-cols-2 gap-8">
                {articles.map((article) => (
                  <article key={article.id} className="bg-white rounded-lg shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
                    {/* Image */}
                    <div className="aspect-video overflow-hidden">
                      <img
                        src={article.featured_image}
                        alt={article.title}
                        className="w-full h-full object-cover hover:scale-105 transition-transform duration-300"
                      />
                    </div>
                    
                    {/* Content */}
                    <div className="p-6">
                      {/* Category & Meta */}
                      <div className="flex items-center justify-between mb-3">
                        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getCategoryColor(article.category)}`}>
                          {article.category}
                        </span>
                        <div className="flex items-center text-sm text-gray-500 space-x-3">
                          <span>👁️ {article.view_count}</span>
                          <span>⏱️ {article.reading_time} min</span>
                        </div>
                      </div>
                      
                      {/* Title */}
                      <h2 className="text-xl font-bold text-gray-900 mb-3 line-clamp-2">
                        {article.title}
                      </h2>
                      
                      {/* Excerpt */}
                      <p className="text-gray-600 mb-4 line-clamp-3">
                        {article.excerpt}
                      </p>
                      
                      {/* Date & Read More */}
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-gray-500">
                          📅 {formatDate(article.published_date)}
                        </span>
                        <Link
                          to={`/blog/${article.slug}`}
                          className="inline-flex items-center text-blue-600 font-semibold hover:text-blue-700 transition-colors"
                        >
                          Lire la suite
                          <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </Link>
                      </div>
                    </div>
                  </article>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BlogPage;