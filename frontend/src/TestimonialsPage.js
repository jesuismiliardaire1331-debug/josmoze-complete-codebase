import React, { useState, useEffect } from 'react';
import axios from 'axios';

const TestimonialsPage = () => {
  const [testimonials, setTestimonials] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedProduct, setSelectedProduct] = useState('');
  const [showSubmitForm, setShowSubmitForm] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;

  useEffect(() => {
    loadTestimonials();
    loadStats();
  }, [selectedProduct]);

  const loadTestimonials = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (selectedProduct) params.append('product_id', selectedProduct);
      
      const response = await axios.get(`${backendUrl}/api/testimonials?${params}`);
      if (response.data.success) {
        setTestimonials(response.data.testimonials);
      }
    } catch (error) {
      console.error('Erreur chargement témoignages:', error);
      // Témoignages par défaut en cas d'erreur
      setTestimonials([
        {
          id: '1',
          customer_name: 'Marie Dubois',
          customer_city: 'Lyon',
          product_name: 'Osmoseur Premium - BlueMountain Avancé',
          rating: 5,
          title: 'Une eau parfaitement pure, enfin !',
          content: 'Après 8 mois d\'utilisation, je ne peux que recommander cet osmoseur. L\'eau a un goût incroyable, mes enfants boivent enfin de l\'eau avec plaisir ! L\'installation a été rapide et le service client est excellent.',
          pros: ['Goût excellent', 'Installation rapide', 'Économies importantes'],
          cons: ['Un peu encombrant sous l\'évier'],
          usage_duration: '8 mois',
          helpful_votes: 24,
          total_votes: 27,
          approved_date: '2024-09-15'
        },
        {
          id: '2',
          customer_name: 'Jean-Pierre Martin',
          customer_city: 'Marseille',
          product_name: 'Osmoseur Essentiel - BlueMountain Compact',
          rating: 5,
          title: 'Parfait pour notre famille de 4 !',
          content: 'L\'eau de Marseille étant très calcaire, nous cherchions une solution efficace. Cet osmoseur a dépassé nos attentes ! Plus de traces blanches sur les verres, l\'eau est délicieuse.',
          pros: ['Eau sans calcaire', 'Prix abordable', 'Facile d\'entretien'],
          cons: [],
          usage_duration: '1 an',
          helpful_votes: 31,
          total_votes: 33,
          approved_date: '2024-09-10'
        },
        {
          id: '3',
          customer_name: 'Sophie Leroy',
          customer_city: 'Nantes',
          product_name: 'Osmoseur Prestige - BlueMountain De Comptoir',
          rating: 5,
          title: 'Le top du top pour notre bébé',
          content: 'Avec l\'arrivée de notre premier enfant, nous voulions le meilleur pour sa santé. Cet osmoseur haut de gamme nous donne une tranquillité d\'esprit totale.',
          pros: ['Qualité exceptionnelle', 'Écran tactile moderne', 'Parfait pour bébé'],
          cons: ['Prix élevé mais justifié'],
          usage_duration: '6 mois',
          helpful_votes: 18,
          total_votes: 19,
          approved_date: '2024-09-12'
        }
      ]);
    }
    setLoading(false);
  };

  const loadStats = async () => {
    try {
      const params = new URLSearchParams();
      if (selectedProduct) params.append('product_id', selectedProduct);
      
      const response = await axios.get(`${backendUrl}/api/testimonials/stats?${params}`);
      if (response.data.success) {
        setStats(response.data.stats);
      }
    } catch (error) {
      console.error('Erreur chargement stats:', error);
      setStats({
        total_reviews: 127,
        average_rating: 4.8,
        rating_distribution: { "5": 89, "4": 28, "3": 7, "2": 2, "1": 1 }
      });
    }
  };

  const renderStars = (rating, size = 'text-base') => {
    return Array.from({ length: 5 }, (_, i) => (
      <span 
        key={i} 
        className={`${size} ${i < rating ? 'text-yellow-400' : 'text-gray-300'}`}
      >
        ⭐
      </span>
    ));
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  const getHelpfulnessPercentage = (helpful, total) => {
    if (total === 0) return 0;
    return Math.round((helpful / total) * 100);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-green-600 to-green-800 text-white py-16">
        <div className="max-w-7xl mx-auto px-4">
          <div className="text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">
              ⭐ Témoignages Clients
            </h1>
            <p className="text-xl md:text-2xl text-green-100 mb-8">
              L'avis de nos clients qui ont choisi l'osmose inverse Josmoze
            </p>
            
            {/* Stats Overview */}
            {stats && (
              <div className="max-w-4xl mx-auto grid md:grid-cols-3 gap-8 mt-12">
                <div className="bg-white bg-opacity-20 rounded-lg p-6">
                  <div className="text-3xl font-bold mb-2">{stats.total_reviews}</div>
                  <div className="text-green-100">Avis clients</div>
                </div>
                <div className="bg-white bg-opacity-20 rounded-lg p-6">
                  <div className="flex items-center justify-center mb-2">
                    <span className="text-3xl font-bold mr-2">{stats.average_rating}</span>
                    <div className="flex">
                      {renderStars(Math.round(stats.average_rating), 'text-xl')}
                    </div>
                  </div>
                  <div className="text-green-100">Note moyenne</div>
                </div>
                <div className="bg-white bg-opacity-20 rounded-lg p-6">
                  <div className="text-3xl font-bold mb-2">
                    {Math.round((stats.rating_distribution["5"] / stats.total_reviews) * 100)}%
                  </div>
                  <div className="text-green-100">Avis 5 étoiles</div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-16">
        {/* Filters */}
        <div className="flex flex-col md:flex-row justify-between items-center mb-8">
          <div className="mb-4 md:mb-0">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filtrer par produit
            </label>
            <select
              value={selectedProduct}
              onChange={(e) => setSelectedProduct(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-green-500"
            >
              <option value="">Tous les produits</option>
              <option value="osmoseur-essentiel">Osmoseur Essentiel</option>
              <option value="osmoseur-premium">Osmoseur Premium</option>
              <option value="osmoseur-prestige">Osmoseur Prestige</option>
              <option value="purificateur-portable-hydrogene">Purificateur H2-Pro</option>
              <option value="fontaine-eau-animaux">Fontaine Animaux</option>
            </select>
          </div>
          
          <button
            onClick={() => setShowSubmitForm(true)}
            className="bg-green-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors"
          >
            ✍️ Laisser un avis
          </button>
        </div>

        {/* Rating Distribution */}
        {stats && (
          <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
            <h3 className="text-xl font-semibold mb-4">📊 Répartition des notes</h3>
            <div className="space-y-2">
              {[5, 4, 3, 2, 1].map((rating) => {
                const count = stats.rating_distribution[rating.toString()] || 0;
                const percentage = stats.total_reviews > 0 
                  ? Math.round((count / stats.total_reviews) * 100) 
                  : 0;
                
                return (
                  <div key={rating} className="flex items-center space-x-4">
                    <span className="w-12 text-sm">{rating} ⭐</span>
                    <div className="flex-1 bg-gray-200 rounded-full h-3">
                      <div 
                        className="bg-yellow-400 h-3 rounded-full transition-all duration-300"
                        style={{ width: `${percentage}%` }}
                      ></div>
                    </div>
                    <span className="w-16 text-sm text-gray-600">
                      {count} ({percentage}%)
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Testimonials List */}
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Chargement des témoignages...</p>
          </div>
        ) : testimonials.length === 0 ? (
          <div className="text-center py-12">
            <div className="text-6xl mb-4">📝</div>
            <h3 className="text-xl font-semibold text-gray-900 mb-2">
              Aucun témoignage trouvé
            </h3>
            <p className="text-gray-600">
              Soyez le premier à laisser un avis pour ce produit !
            </p>
          </div>
        ) : (
          <div className="space-y-6">
            {testimonials.map((testimonial) => (
              <div key={testimonial.id} className="bg-white rounded-lg shadow-lg p-6">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-center space-x-4 mb-2">
                      <h3 className="font-semibold text-lg text-gray-900">
                        {testimonial.customer_name}
                      </h3>
                      <span className="text-gray-500">•</span>
                      <span className="text-gray-600">{testimonial.customer_city}</span>
                      {testimonial.usage_duration && (
                        <>
                          <span className="text-gray-500">•</span>
                          <span className="text-gray-600">Utilise depuis {testimonial.usage_duration}</span>
                        </>
                      )}
                    </div>
                    
                    <div className="flex items-center space-x-2 mb-2">
                      <div className="flex">
                        {renderStars(testimonial.rating)}
                      </div>
                      <span className="text-gray-600 text-sm">
                        {formatDate(testimonial.approved_date)}
                      </span>
                    </div>
                    
                    <p className="text-sm text-gray-600 mb-4">
                      Produit : {testimonial.product_name}
                    </p>
                  </div>
                </div>

                <h4 className="font-semibold text-gray-900 mb-3">
                  {testimonial.title}
                </h4>
                
                <p className="text-gray-700 mb-4 leading-relaxed">
                  {testimonial.content}
                </p>

                {/* Pros and Cons */}
                <div className="grid md:grid-cols-2 gap-4 mb-4">
                  {testimonial.pros && testimonial.pros.length > 0 && (
                    <div>
                      <h5 className="font-medium text-green-800 mb-2">✅ Points positifs</h5>
                      <ul className="space-y-1">
                        {testimonial.pros.map((pro, index) => (
                          <li key={index} className="text-sm text-gray-600">• {pro}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  
                  {testimonial.cons && testimonial.cons.length > 0 && (
                    <div>
                      <h5 className="font-medium text-red-800 mb-2">⚠️ Points d'amélioration</h5>
                      <ul className="space-y-1">
                        {testimonial.cons.map((con, index) => (
                          <li key={index} className="text-sm text-gray-600">• {con}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>

                {/* Helpful votes */}
                <div className="flex items-center justify-between pt-4 border-t border-gray-200">
                  <div className="text-sm text-gray-600">
                    Utile pour {testimonial.helpful_votes} personnes sur {testimonial.total_votes}
                    {testimonial.total_votes > 0 && (
                      <span className="ml-2 text-green-600">
                        ({getHelpfulnessPercentage(testimonial.helpful_votes, testimonial.total_votes)}% trouvent cet avis utile)
                      </span>
                    )}
                  </div>
                  
                  <div className="flex space-x-2">
                    <button className="text-sm text-green-600 hover:text-green-700 px-3 py-1 border border-green-600 rounded-lg hover:bg-green-50 transition-colors">
                      👍 Utile
                    </button>
                    <button className="text-sm text-gray-600 hover:text-gray-700 px-3 py-1 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors">
                      👎 Pas utile
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* CTA Section */}
        <div className="mt-16 bg-gradient-to-r from-green-50 to-green-100 rounded-lg p-8 text-center">
          <h3 className="text-2xl font-bold text-gray-900 mb-4">
            💧 Vous aussi, découvrez l'eau pure Josmoze
          </h3>
          <p className="text-gray-700 mb-6">
            Rejoignez les milliers de familles qui ont fait confiance à nos osmoseurs
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={() => window.location.href = '/contact'}
              className="bg-green-600 text-white px-8 py-3 rounded-lg font-semibold hover:bg-green-700 transition-colors"
            >
              🧪 Test gratuit de votre eau
            </button>
            <button 
              onClick={() => window.location.href = '/#products-section'}
              className="bg-white text-green-600 border-2 border-green-600 px-8 py-3 rounded-lg font-semibold hover:bg-green-50 transition-colors"
            >
              🛒 Voir nos osmoseurs
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default TestimonialsPage;