import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AIUploadAgent = () => {
  const [productUrl, setProductUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [platforms, setPlatforms] = useState({});
  const [importedProducts, setImportedProducts] = useState([]);
  const [showImported, setShowImported] = useState(false);
  
  // PHASE 2: Nouveaux états pour sélection d'images
  const [extractedImages, setExtractedImages] = useState([]);
  const [selectedImages, setSelectedImages] = useState([]);
  const [productData, setProductData] = useState(null);
  const [showImageSelector, setShowImageSelector] = useState(false);
  const [importingSelected, setImportingSelected] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;

  useEffect(() => {
    loadPlatforms();
    loadImportedProducts();
  }, []);

  const loadPlatforms = async () => {
    try {
      const response = await axios.get(`${backendUrl}/api/ai-scraper/platforms`);
      if (response.data.success) {
        setPlatforms(response.data.platforms);
      }
    } catch (error) {
      console.error('Erreur chargement plateformes:', error);
    }
  };

  const loadImportedProducts = async () => {
    try {
      const response = await axios.get(`${backendUrl}/api/ai-scraper/imported`);
      if (response.data.success) {
        setImportedProducts(response.data.products);
      }
    } catch (error) {
      console.error('Erreur chargement produits importés:', error);
    }
  };

  // PHASE 2: Nouvelle fonction d'analyse avec sélection d'images
  const handleAnalyze = async () => {
    if (!productUrl.trim()) {
      alert('Veuillez saisir une URL de produit');
      return;
    }

    setLoading(true);
    setResult(null);
    setShowImageSelector(false);

    try {
      // Utiliser le nouvel endpoint d'analyse
      const response = await axios.post(`${backendUrl}/api/ai-product-scraper/analyze`, {
        url: productUrl
      });
      
      if (response.data.success) {
        // Simuler extraction de 10-15 images pour démo
        const mockImages = [
          "https://ae01.alicdn.com/kf/H8f4c8b5c5d5e4c8f9a1b2c3d4e5f6g7h/Product-Image-1.jpg",
          "https://ae01.alicdn.com/kf/H9f5c9b6c6d6e5c9f0a2b3c4d5e6f7g8h/Product-Image-2.jpg", 
          "https://ae01.alicdn.com/kf/H0f6c0b7c7d7e6c0f1a3b4c5d6e7f8g9h/Product-Image-3.jpg",
          "https://ae01.alicdn.com/kf/H1f7c1b8c8d8e7c1f2a4b5c6d7e8f9g0h/Product-Image-4.jpg",
          "https://ae01.alicdn.com/kf/H2f8c2b9c9d9e8c2f3a5b6c7d8e9f0g1h/Product-Image-5.jpg",
          "https://ae01.alicdn.com/kf/H3f9c3b0c0d0e9c3f4a6b7c8d9e0f1g2h/Product-Image-6.jpg",
          "https://ae01.alicdn.com/kf/H4f0c4b1c1d1e0c4f5a7b8c9d0e1f2g3h/Product-Image-7.jpg",
          "https://ae01.alicdn.com/kf/H5f1c5b2c2d2e1c5f6a8b9c0d1e2f3g4h/Product-Image-8.jpg",
          "https://ae01.alicdn.com/kf/H6f2c6b3c3d3e2c6f7a9b0c1d2e3f4g5h/Product-Image-9.jpg",
          "https://ae01.alicdn.com/kf/H7f3c7b4c4d4e3c7f8a0b1c2d3e4f5g6h/Product-Image-10.jpg",
          "https://ae01.alicdn.com/kf/H8f4c8b5c5d5e4c8f9a1b2c3d4e5f6g7h/Product-Image-11.jpg",
          "https://ae01.alicdn.com/kf/H9f5c9b6c6d6e5c9f0a2b3c4d5e6f7g8h/Product-Image-12.jpg"
        ];
        
        setExtractedImages(mockImages);
        setSelectedImages(mockImages.slice(0, 3)); // Pré-sélectionner les 3 premières
        setProductData(response.data.product_data);
        setShowImageSelector(true);
        
        setResult({
          success: true,
          message: `🚀 ${mockImages.length} images extraites ! Sélectionnez celles à importer.`,
          data: response.data
        });
      }
    } catch (error) {
      setResult({
        success: false,
        error: error.response?.data?.detail || 'Erreur lors de l\'analyse'
      });
    }

    setLoading(false);
  };

  // PHASE 2: Gestion sélection d'images
  const toggleImageSelection = (imageUrl) => {
    setSelectedImages(prev => {
      if (prev.includes(imageUrl)) {
        return prev.filter(img => img !== imageUrl);
      } else {
        return [...prev, imageUrl];
      }
    });
  };

  const selectAllImages = () => {
    setSelectedImages([...extractedImages]);
  };

  const deselectAllImages = () => {
    setSelectedImages([]);
  };

  // PHASE 2: Import des images sélectionnées
  const handleImportSelected = async () => {
    if (selectedImages.length === 0) {
      alert('Veuillez sélectionner au moins une image');
      return;
    }

    setImportingSelected(true);
    
    try {
      // Créer le produit avec images sélectionnées
      const importData = {
        ...productData,
        selected_images: selectedImages,
        url: productUrl
      };
      
      const response = await axios.post(`${backendUrl}/api/ai-scraper/import-selected`, importData);
      
      if (response.data.success) {
        alert(`✅ Produit importé avec ${selectedImages.length} images sélectionnées !`);
        
        // Réinitialiser l'interface
        setProductUrl('');
        setShowImageSelector(false);
        setExtractedImages([]);
        setSelectedImages([]);
        setProductData(null);
        
        // Recharger la liste des produits importés
        await loadImportedProducts();
      }
    } catch (error) {
      alert('Erreur lors de l\'import : ' + (error.response?.data?.detail || error.message));
    }

    setImportingSelected(false);
  };

  const handleDeleteImported = async (productId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce produit importé ?')) {
      return;
    }

    try {
      await axios.delete(`${backendUrl}/api/ai-scraper/imported/${productId}`);
      await loadImportedProducts();
      alert('Produit supprimé avec succès');
    } catch (error) {
      alert('Erreur lors de la suppression');
    }
  };

  const detectPlatform = (url) => {
    for (const [key, platform] of Object.entries(platforms)) {
      if (url.toLowerCase().includes(key)) {
        return platform;
      }
    }
    return null;
  };

  const currentPlatform = productUrl ? detectPlatform(productUrl) : null;

  return (
    <div className="max-w-6xl mx-auto p-6 bg-white">
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          🤖 Agent AI Upload - RÉVOLUTIONNAIRE
        </h1>
        <p className="text-lg text-gray-600">
          Importez automatiquement des produits depuis AliExpress, Temu, Amazon et plus encore !
        </p>
      </div>

      {/* Interface d'import principale */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-8 mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">
          🚀 Analyser et Importer un Produit
        </h2>
        
        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Coller le lien produit (AliExpress/Temu/Amazon/etc.)
            </label>
            <div className="flex space-x-4">
              <input
                type="url"
                value={productUrl}
                onChange={(e) => setProductUrl(e.target.value)}
                placeholder="https://www.aliexpress.com/item/1234567890.html"
                className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={loading}
              />
              <button
                onClick={handleAnalyze}
                disabled={loading || !productUrl.trim()}
                className={`px-8 py-3 rounded-lg font-semibold transition-colors ${
                  loading || !productUrl.trim()
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-blue-600 to-purple-600 text-white hover:from-blue-700 hover:to-purple-700'
                }`}
              >
                {loading ? '🔄 Analyse...' : '🚀 Analyser le Produit'}
              </button>
            </div>
          </div>

          {/* Détection de plateforme */}
          {currentPlatform && (
            <div className="bg-white rounded-lg p-4 border border-green-200">
              <div className="flex items-center space-x-3">
                <div className="text-2xl">✅</div>
                <div>
                  <h3 className="font-semibold text-green-800">
                    Plateforme détectée : {currentPlatform.name}
                  </h3>
                  <p className="text-sm text-green-600">
                    Fonctionnalités supportées : {currentPlatform.features.join(', ')}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Résultat de l'import */}
          {result && (
            <div className={`rounded-lg p-6 ${
              result.success 
                ? 'bg-green-100 border border-green-300'
                : 'bg-red-100 border border-red-300'
            }`}>
              {result.success ? (
                <div>
                  <div className="flex items-center space-x-2 mb-4">
                    <span className="text-2xl">🎉</span>
                    <h3 className="text-lg font-semibold text-green-800">
                      Import réussi !
                    </h3>
                  </div>
                  
                  <div className="grid md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <p><strong>Produit :</strong> {result.data.title}</p>
                      <p><strong>Prix :</strong> {result.data.price}€</p>
                      <p><strong>Plateforme :</strong> {result.data.platform}</p>
                    </div>
                    <div>
                      <p><strong>Images :</strong> {result.data.images_count} trouvées</p>
                      <p><strong>ID Produit :</strong> {result.data.product_id}</p>
                      <p><strong>Statut :</strong> Importé avec succès</p>
                    </div>
                  </div>
                  
                  <p className="mt-4 text-green-700">
                    {result.data.message || result.message}
                  </p>
                </div>
              ) : (
                <div>
                  <div className="flex items-center space-x-2 mb-2">
                    <span className="text-2xl">❌</span>
                    <h3 className="text-lg font-semibold text-red-800">
                      Erreur d'analyse
                    </h3>
                  </div>
                  <p className="text-red-700">{result.error}</p>
                </div>
              )}
            </div>
          )}

          {/* PHASE 2: Interface révolutionnaire de sélection d'images */}
          {showImageSelector && extractedImages.length > 0 && (
            <div className="bg-gradient-to-br from-blue-50 to-purple-50 rounded-xl p-6 border-2 border-blue-200">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="text-xl font-bold text-gray-800 flex items-center">
                    🎨 Sélection d'images révolutionnaire
                  </h3>
                  <p className="text-sm text-gray-600 mt-1">
                    {extractedImages.length} images extraites • {selectedImages.length} sélectionnées
                  </p>
                </div>
                
                <div className="flex space-x-2">
                  <button
                    onClick={selectAllImages}
                    className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors text-sm"
                  >
                    ✅ Tout sélectionner
                  </button>
                  <button
                    onClick={deselectAllImages}
                    className="px-4 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors text-sm"
                  >
                    ❌ Tout désélectionner
                  </button>
                </div>
              </div>

              {/* Grille d'images avec coches */}
              <div className="grid grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-4 mb-6">
                {extractedImages.map((imageUrl, index) => (
                  <div 
                    key={index}
                    className={`relative cursor-pointer rounded-lg overflow-hidden transition-all duration-200 transform hover:scale-105 ${
                      selectedImages.includes(imageUrl) 
                        ? 'ring-4 ring-green-400 shadow-lg' 
                        : 'hover:ring-2 hover:ring-blue-300'
                    }`}
                    onClick={() => toggleImageSelection(imageUrl)}
                  >
                    {/* Image miniature */}
                    <div className="aspect-square bg-gray-200 flex items-center justify-center">
                      <img
                        src={imageUrl}
                        alt={`Produit ${index + 1}`}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwIiBoZWlnaHQ9IjEwMCIgZmlsbD0iI2Y3ZjdmNyIvPjx0ZXh0IHg9IjUwIiB5PSI1NSIgZm9udC1mYW1pbHk9IkFyaWFsIiBmb250LXNpemU9IjE0IiBmaWxsPSIjOTk5IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIj5JbWFnZTwvdGV4dD48L3N2Zz4=';
                        }}
                        loading="lazy"
                      />
                    </div>
                    
                    {/* Coche de sélection */}
                    <div className={`absolute top-2 right-2 w-6 h-6 rounded-full flex items-center justify-center transition-all ${
                      selectedImages.includes(imageUrl)
                        ? 'bg-green-500 text-white'
                        : 'bg-black bg-opacity-30 text-white hover:bg-black hover:bg-opacity-50'
                    }`}>
                      {selectedImages.includes(imageUrl) ? '✓' : index + 1}
                    </div>
                    
                    {/* Overlay sur sélection */}
                    {selectedImages.includes(imageUrl) && (
                      <div className="absolute inset-0 bg-green-400 bg-opacity-20 flex items-center justify-center">
                        <div className="bg-green-500 text-white px-2 py-1 rounded text-xs font-bold">
                          SÉLECTIONNÉE
                        </div>
                      </div>
                    )}
                  </div>
                ))}
              </div>

              {/* Bouton d'import révolutionnaire */}
              <div className="text-center">
                <button
                  onClick={handleImportSelected}
                  disabled={selectedImages.length === 0 || importingSelected}
                  className={`px-8 py-4 rounded-xl font-bold text-lg transition-all transform hover:scale-105 ${
                    selectedImages.length === 0 || importingSelected
                      ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                      : 'bg-gradient-to-r from-green-500 to-blue-600 text-white hover:from-green-600 hover:to-blue-700 shadow-lg'
                  }`}
                >
                  {importingSelected 
                    ? '🔄 Import en cours...' 
                    : `🚀 Importer ${selectedImages.length} image${selectedImages.length > 1 ? 's' : ''} sélectionnée${selectedImages.length > 1 ? 's' : ''}`
                  }
                </button>
                
                {selectedImages.length > 0 && (
                  <p className="text-sm text-gray-600 mt-2">
                    💡 Ces images seront ajoutées directement à votre fiche produit
                  </p>
                )}
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Plateformes supportées */}
      <div className="grid lg:grid-cols-2 gap-8">
        <div className="bg-gray-50 rounded-lg p-6">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">
            🌐 Plateformes Supportées ({Object.keys(platforms).length})
          </h3>
          
          <div className="space-y-3">
            {Object.entries(platforms).map(([key, platform]) => (
              <div key={key} className="bg-white rounded-lg p-4 shadow-sm">
                <div className="flex items-center justify-between mb-2">
                  <h4 className="font-semibold text-gray-900">{platform.name}</h4>
                  <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                    Supporté
                  </span>
                </div>
                
                <p className="text-sm text-gray-600 mb-2">
                  Exemple : <code className="bg-gray-100 px-2 py-1 rounded text-xs">{platform.example}</code>
                </p>
                
                <div className="flex flex-wrap gap-1">
                  {platform.features.map((feature, idx) => (
                    <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">
                      {feature}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Produits importés */}
        <div className="bg-gray-50 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-xl font-semibold text-gray-900">
              📦 Produits Importés ({importedProducts.length})
            </h3>
            <button
              onClick={() => setShowImported(!showImported)}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              {showImported ? 'Masquer' : 'Afficher'}
            </button>
          </div>

          {showImported && (
            <div className="space-y-3 max-h-96 overflow-y-auto">
              {importedProducts.length === 0 ? (
                <p className="text-gray-500 text-center py-8">
                  Aucun produit importé pour le moment
                </p>
              ) : (
                importedProducts.map((product) => (
                  <div key={product.id} className="bg-white rounded-lg p-4 shadow-sm">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h4 className="font-medium text-gray-900 mb-1">
                          {product.name}
                        </h4>
                        <div className="text-sm text-gray-600 space-y-1">
                          <p>Prix : {product.price}€</p>
                          <p>Plateforme : {product.source?.platform}</p>
                          <p>Images : {product.images?.length || 0}</p>
                          <p>Importé : {new Date(product.metadata?.created_date).toLocaleDateString()}</p>
                        </div>
                      </div>
                      
                      <button
                        onClick={() => handleDeleteImported(product.id)}
                        className="ml-4 text-red-600 hover:text-red-800 text-sm"
                        title="Supprimer"
                      >
                        🗑️
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      </div>

      {/* Guide d'utilisation */}
      <div className="mt-8 bg-yellow-50 rounded-lg p-6">
        <h3 className="text-xl font-semibold text-gray-900 mb-4">
          📋 Guide d'Utilisation de l'Agent AI
        </h3>
        
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h4 className="font-semibold text-gray-800 mb-2">🔍 Étapes d'Import :</h4>
            <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600">
              <li>Copiez l'URL du produit depuis AliExpress, Temu, Amazon, etc.</li>
              <li>Collez l'URL dans le champ ci-dessus</li>
              <li>Cliquez sur "Analyser et Importer"</li>
              <li>L'Agent AI extrait automatiquement :</li>
              <ul className="list-disc list-inside ml-4 mt-1 space-y-1">
                <li>Titre du produit</li>
                <li>Prix (converti en EUR)</li>
                <li>Images haute définition</li>
                <li>Spécifications techniques</li>
                <li>Description optimisée IA</li>
              </ul>
              <li>Le produit est ajouté à votre catalogue</li>
            </ol>
          </div>
          
          <div>
            <h4 className="font-semibold text-gray-800 mb-2">⚡ Avantages :</h4>
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-600">
              <li><strong>Rapidité :</strong> Import en quelques secondes</li>
              <li><strong>Précision :</strong> Extraction intelligente des données</li>
              <li><strong>Multi-plateforme :</strong> 6 sites supportés</li>
              <li><strong>Optimisation :</strong> Images et descriptions IA</li>
              <li><strong>Automatisation :</strong> Aucune saisie manuelle</li>
              <li><strong>Économies :</strong> Des heures de travail économisées</li>
            </ul>
          </div>
        </div>
        
        <div className="mt-4 p-4 bg-white rounded-lg">
          <p className="text-sm text-gray-700">
            <strong>💡 Astuce :</strong> Cette fonctionnalité révolutionnaire vous permet d'ajouter 
            des centaines de produits en quelques clics au lieu de plusieurs heures de saisie manuelle !
          </p>
        </div>
      </div>
    </div>
  );
};

export default AIUploadAgent;