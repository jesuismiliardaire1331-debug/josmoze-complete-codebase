import React, { useState, useEffect } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const ProductRecommendations = ({ 
  customerId, 
  currentCart = [], 
  customerType = "B2C",
  context = {},
  onProductClick,
  maxRecommendations = 4,
  title = "🎯 Recommandations pour vous"
}) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchRecommendations();
  }, [customerId, JSON.stringify(currentCart), customerType]);

  const fetchRecommendations = async () => {
    try {
      setLoading(true);
      setError('');

      const requestData = {
        customer_id: customerId,
        current_cart: currentCart,
        customer_type: customerType,
        context: context,
        max_recommendations: maxRecommendations
      };

      const response = await axios.post(
        `${BACKEND_URL}/api/recommendations/smart`,
        requestData
      );

      if (response.data.success) {
        setRecommendations(response.data.recommendations || []);
      } else {
        setError('Impossible de charger les recommandations');
      }
    } catch (err) {
      console.error('Recommendations fetch error:', err);
      setError('Erreur lors du chargement des recommandations');
    } finally {
      setLoading(false);
    }
  };

  const getRecommendationTypeIcon = (type) => {
    switch (type) {
      case 'collaborative':
        return '👥';
      case 'complementary':
        return '🔗';
      case 'trending':
        return '📈';
      case 'personalized':
      default:
        return '🎯';
    }
  };

  const getRecommendationTypeLabel = (type) => {
    switch (type) {
      case 'collaborative':
        return 'Clients similaires';
      case 'complementary':
        return 'Produits complémentaires';
      case 'trending':
        return 'Populaire';
      case 'personalized':
      default:
        return 'Personnalisé';
    }
  };

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return 'text-green-600 bg-green-50';
    if (confidence >= 0.6) return 'text-blue-600 bg-blue-50';
    if (confidence >= 0.4) return 'text-yellow-600 bg-yellow-50';
    return 'text-gray-600 bg-gray-50';
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">{title}</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {Array(maxRecommendations).fill(0).map((_, index) => (
            <div key={index} className="animate-pulse">
              <div className="bg-gray-200 h-40 rounded-lg mb-3"></div>
              <div className="bg-gray-200 h-4 rounded mb-2"></div>
              <div className="bg-gray-200 h-3 rounded w-2/3"></div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">{title}</h3>
        <div className="text-center py-8">
          <div className="text-gray-400 text-4xl mb-2">🤷‍♂️</div>
          <p className="text-gray-600">{error}</p>
          <button 
            onClick={fetchRecommendations}
            className="mt-3 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Réessayer
          </button>
        </div>
      </div>
    );
  }

  if (!recommendations.length) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">{title}</h3>
        <div className="text-center py-8">
          <div className="text-gray-400 text-4xl mb-2">🎯</div>
          <p className="text-gray-600">
            Aucune recommandation disponible pour le moment
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-xl font-semibold text-gray-900">{title}</h3>
        <div className="text-sm text-gray-500">
          {recommendations.length} suggestion{recommendations.length > 1 ? 's' : ''}
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {recommendations.map((rec, index) => {
          const product = rec.product;
          const confidence = rec.confidence || 0.5;
          const reasons = rec.reasons || [];
          const type = rec.recommendation_type || 'personalized';

          return (
            <div
              key={`${product.id}-${index}`}
              className="group cursor-pointer transform hover:scale-105 transition-all duration-200"
              onClick={() => onProductClick && onProductClick(product)}
            >
              {/* Carte produit */}
              <div className="bg-white border border-gray-200 rounded-lg overflow-hidden shadow-sm hover:shadow-md transition-shadow">
                
                {/* Badge de recommandation */}
                <div className="relative">
                  <div className="absolute top-2 left-2 z-10">
                    <span className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${getConfidenceColor(confidence)}`}>
                      {getRecommendationTypeIcon(type)} {getRecommendationTypeLabel(type)}
                    </span>
                  </div>
                  
                  {/* Badge confiance */}
                  <div className="absolute top-2 right-2 z-10">
                    <div className="bg-black bg-opacity-70 text-white px-2 py-1 rounded text-xs">
                      {Math.round(confidence * 100)}% match
                    </div>
                  </div>

                  {/* Image produit */}
                  <div className="h-48 bg-gray-100 flex items-center justify-center overflow-hidden">
                    {product.image ? (
                      <img
                        src={product.image}
                        alt={product.name}
                        className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-300"
                        onError={(e) => {
                          e.target.src = 'https://via.placeholder.com/300x200?text=Image+Non+Disponible';
                        }}
                      />
                    ) : (
                      <div className="text-gray-400 text-4xl">📦</div>
                    )}
                  </div>
                </div>

                {/* Contenu */}
                <div className="p-4">
                  <h4 className="font-semibold text-gray-900 mb-2 line-clamp-2 group-hover:text-blue-600 transition-colors">
                    {product.name}
                  </h4>
                  
                  <div className="mb-3">
                    <div className="flex items-center justify-between">
                      <span className="text-2xl font-bold text-blue-600">
                        {product.price?.toFixed(2)}€
                      </span>
                      {product.original_price && product.original_price > product.price && (
                        <span className="text-sm text-gray-500 line-through">
                          {product.original_price.toFixed(2)}€
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Raisons de la recommandation */}
                  <div className="mb-3">
                    <div className="text-xs text-gray-600">
                      <span className="font-medium">Pourquoi ce produit :</span>
                    </div>
                    <div className="mt-1">
                      {reasons.slice(0, 2).map((reason, idx) => (
                        <div key={idx} className="text-xs text-gray-500 flex items-center">
                          <span className="mr-1">•</span>
                          <span>{reason}</span>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Bouton d'action */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      if (onProductClick) onProductClick(product);
                    }}
                    className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium"
                  >
                    Voir le produit
                  </button>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Footer informatif */}
      <div className="mt-6 pt-4 border-t border-gray-200">
        <div className="flex items-center justify-between text-xs text-gray-500">
          <span>
            Recommandations basées sur l'IA et l'analyse comportementale
          </span>
          <button
            onClick={fetchRecommendations}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            🔄 Actualiser
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProductRecommendations;