import React, { useState, useEffect } from 'react';

const ProductQuestionnaire = ({ isOpen, onClose, onRecommendation, formatPrice }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({
    household_size: '',
    housing_type: '',
    skill_level: '',
    budget: '',
    shower_interest: ''
  });
  const [showResults, setShowResults] = useState(false);
  const [recommendation, setRecommendation] = useState(null);

  // Fonction formatPrice par défaut si non fournie
  const defaultFormatPrice = (price) => `${price.toFixed(2)}€`;

  const questions = [
    {
      id: 'household_size',
      question: 'Combien de personnes dans votre foyer ?',
      options: [
        { value: '1-2', label: '1-2 personnes' },
        { value: '3-4', label: '3-4 personnes' },
        { value: '5+', label: '5+ personnes' }
      ]
    },
    {
      id: 'housing_type',
      question: 'Type de logement ?',
      options: [
        { value: 'appartement', label: 'Appartement' },
        { value: 'maison', label: 'Maison' },
        { value: 'bureau', label: 'Bureau' }
      ]
    },
    {
      id: 'skill_level',
      question: 'Niveau de bricolage ?',
      options: [
        { value: 'debutant', label: 'Débutant' },
        { value: 'notions', label: 'Quelques notions' },
        { value: 'expert', label: 'Expert' }
      ]
    },
    {
      id: 'budget',
      question: 'Budget approximatif ?',
      options: [
        { value: '200-400', label: '200€ - 400€' },
        { value: '400-700', label: '400€ - 700€' },
        { value: '700+', label: '700€+' }
      ]
    },
    {
      id: 'shower_interest',
      question: 'En plus de votre eau de boisson, seriez-vous intéressé(e) par l\'amélioration de la qualité de l\'eau de votre douche pour prendre soin de votre peau et de vos cheveux ?',
      options: [
        { value: 'oui', label: 'Oui, cela m\'intéresse' },
        { value: 'non', label: 'Non, merci' }
      ]
    }
  ];

  const getRecommendation = (answers) => {
    // Logique de recommandation basée sur les réponses
    const { household_size, housing_type, skill_level, budget, shower_interest } = answers;
    
    // Recommandation osmoseur principal
    let mainRecommendation;
    if (budget === '700+') {
      mainRecommendation = {
        id: 'osmoseur-prestige',
        name: 'Osmoseur Prestige - BlueMountain De Comptoir', 
        price: 899.0,
        reason: 'Parfait pour votre budget et besoins premium'
      };
    } else if (budget === '400-700') {
      mainRecommendation = {
        id: 'osmoseur-premium',
        name: 'Osmoseur Premium - BlueMountain Avancé',
        price: 549.0,
        reason: 'Excellent rapport qualité-prix pour votre situation'
      };
    } else if (budget === '200-400') {
      mainRecommendation = {
        id: 'osmoseur-essentiel',
        name: 'Osmoseur Essentiel - BlueMountain Compact',
        price: 449.0,
        reason: 'Solution efficace et économique'
      };
    } else {
      // Par défaut Premium
      mainRecommendation = {
        id: 'osmoseur-premium',
        name: 'Osmoseur Premium - BlueMountain Avancé',
        price: 549.0,
        reason: 'Notre meilleure vente, adapté à la plupart des foyers'
      };
    }

    // Ajouter le filtre douche si intéressé
    if (shower_interest === 'oui') {
      return {
        ...mainRecommendation,
        showerFilter: {
          id: 'filtre-purificateur-douche-anti-calcaire',
          name: 'Filtre Purificateur de Douche Anti-Calcaire',
          price: 39.90,
          reason: 'Pour une peau plus douce et des cheveux plus brillants'
        },
        totalPrice: mainRecommendation.price + 39.90,
        hasBundle: true
      };
    }
    
    return mainRecommendation;
  };

  const handleAnswer = (value) => {
    const newAnswers = { ...answers, [questions[currentQuestion].id]: value };
    setAnswers(newAnswers);

    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      // Calculer la recommandation
      const rec = getRecommendation(newAnswers);
      setRecommendation(rec);
      setShowResults(true);
    }
  };

  const handleRestart = () => {
    setCurrentQuestion(0);
    setAnswers({
      household_size: '',
      housing_type: '',
      skill_level: '',
      budget: ''
    });
    setShowResults(false);
    setRecommendation(null);
  };

  const handleClose = () => {
    if (onRecommendation && recommendation) {
      onRecommendation(recommendation);
    }
    onClose();
    // Reset après fermeture
    setTimeout(() => {
      handleRestart();
    }, 300);
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg max-w-md w-full p-6 relative">
        {/* Bouton fermer */}
        <button
          onClick={handleClose}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 text-2xl"
        >
          ×
        </button>

        {!showResults ? (
          <>
            {/* En-tête questionnaire */}
            <div className="mb-6">
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                💧 Trouvez votre osmoseur idéal
              </h3>
              <div className="bg-blue-100 rounded-full h-2 mb-2">
                <div 
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-600">
                Question {currentQuestion + 1} sur {questions.length}
              </p>
            </div>

            {/* Question actuelle */}
            <div className="mb-6">
              <h4 className="text-lg font-semibold text-gray-800 mb-4">
                {questions[currentQuestion].question}
              </h4>
              
              <div className="space-y-3">
                {questions[currentQuestion].options.map((option) => (
                  <button
                    key={option.value}
                    onClick={() => handleAnswer(option.value)}
                    className="w-full p-3 text-left border rounded-lg hover:bg-blue-50 hover:border-blue-300 transition-colors"
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>
          </>
        ) : (
          <>
            {/* Résultats */}
            <div className="text-center mb-6">
              <div className="text-6xl mb-4">🎯</div>
              <h3 className="text-xl font-bold text-gray-900 mb-2">
                Votre osmoseur recommandé !
              </h3>
              <p className="text-gray-600">
                Basé sur vos réponses personnalisées
              </p>
            </div>

            {recommendation && (
              <div className="bg-blue-50 rounded-lg p-4 mb-6">
                <div className="text-center">
                  <h4 className="font-semibold text-gray-900 mb-2">
                    {recommendation.hasBundle ? '🎁 Pack Recommandé' : recommendation.name}
                  </h4>
                  
                  {recommendation.hasBundle ? (
                    <div className="space-y-3 mb-4">
                      {/* Osmoseur principal */}
                      <div className="bg-white rounded p-3">
                        <div className="font-medium text-gray-800">{recommendation.name}</div>
                        <div className="text-blue-600 font-bold">{formatPrice ? formatPrice(recommendation.price) : defaultFormatPrice(recommendation.price)}</div>
                        <div className="text-sm text-gray-600">{recommendation.reason}</div>
                      </div>
                      
                      {/* Filtre douche */}
                      <div className="bg-white rounded p-3">
                        <div className="font-medium text-gray-800">{recommendation.showerFilter.name}</div>
                        <div className="text-green-600 font-bold">{formatPrice ? formatPrice(recommendation.showerFilter.price) : defaultFormatPrice(recommendation.showerFilter.price)}</div>
                        <div className="text-sm text-gray-600">{recommendation.showerFilter.reason}</div>
                      </div>
                      
                      {/* Prix total */}
                      <div className="bg-green-50 rounded p-3 border-2 border-green-200">
                        <div className="font-bold text-green-800">Pack Eau Pure Complète</div>
                        <div className="text-2xl font-bold text-green-600">
                          {formatPrice ? formatPrice(recommendation.totalPrice) : defaultFormatPrice(recommendation.totalPrice)}
                        </div>
                        <div className="text-sm text-green-700">Eau pure pour boire ET se laver !</div>
                      </div>
                    </div>
                  ) : (
                    <div className="mb-4">
                      <div className="text-2xl font-bold text-blue-600 mb-2">
                        {formatPrice ? formatPrice(recommendation.price) : defaultFormatPrice(recommendation.price)}
                      </div>
                      <p className="text-sm text-gray-600 mb-4">
                        {recommendation.reason}
                      </p>
                    </div>
                  )}
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => {
                        // Redirection directe vers la fiche produit
                        window.location.href = `/produit/${recommendation.id}`;
                      }}
                      className="flex-1 bg-blue-600 text-white py-2 px-4 rounded-lg font-medium hover:bg-blue-700"
                    >
                      📦 Voir ce Produit
                    </button>
                    
                    <button
                      onClick={handleRestart}
                      className="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-300"
                    >
                      🔄 Refaire
                    </button>
                  </div>
                </div>
              </div>
            )}

            <button
              onClick={handleClose}
              className="w-full bg-gray-100 text-gray-700 py-2 px-4 rounded-lg font-medium hover:bg-gray-200"
            >
              Fermer
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default ProductQuestionnaire;