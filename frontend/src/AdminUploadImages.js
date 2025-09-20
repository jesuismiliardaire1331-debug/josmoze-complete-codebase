import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AdminUploadImages = () => {
  const [selectedFiles, setSelectedFiles] = useState([]);
  const [productAssociations, setProductAssociations] = useState({});
  const [products, setProducts] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [uploadResults, setUploadResults] = useState([]);
  const [previewMode, setPreviewMode] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;

  // Liste des produits disponibles
  const availableProducts = [
    { id: 'osmoseur-essentiel', name: 'Osmoseur Essentiel (449€)', current_image: 'https://images.unsplash.com/photo-1563453392212-326f5e854473?w=500' },
    { id: 'osmoseur-premium', name: 'Osmoseur Premium (549€)', current_image: 'https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=500' },
    { id: 'osmoseur-prestige', name: 'Osmoseur Prestige (899€)', current_image: 'https://images.unsplash.com/photo-1588200908342-23b585c03e26?w=500' },
    { id: 'filtre-douche', name: 'Filtre Douche (39.90€)', current_image: 'https://images.unsplash.com/photo-1584464491033-06628f3a6b7b?w=500' },
    { id: 'purificateur-h2-pro', name: 'Purificateur H2-Pro (79€)', current_image: 'https://images.unsplash.com/photo-1556075798-4825dfaaf498?w=500' },
    { id: 'fontaine-animaux', name: 'Fontaine Animaux (49€)', current_image: 'https://images.unsplash.com/photo-1601758228041-f3b2795255f1?w=500' }
  ];

  useEffect(() => {
    setProducts(availableProducts);
  }, []);

  // Gestion de la sélection de fichiers
  const handleFileSelect = (event) => {
    const files = Array.from(event.target.files);
    setSelectedFiles(files);
    
    // Initialiser les associations avec le premier produit par défaut
    const initialAssociations = {};
    files.forEach((file, index) => {
      initialAssociations[index] = availableProducts[index % availableProducts.length]?.id || 'osmoseur-essentiel';
    });
    setProductAssociations(initialAssociations);
  };

  // Gestion du drag & drop
  const handleDrop = (event) => {
    event.preventDefault();
    const files = Array.from(event.dataTransfer.files);
    if (files.length > 0) {
      setSelectedFiles([...selectedFiles, ...files]);
    }
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  // Mise à jour de l'association produit
  const updateProductAssociation = (fileIndex, productId) => {
    setProductAssociations(prev => ({
      ...prev,
      [fileIndex]: productId
    }));
  };

  // Upload et remplacement des images
  const handleUploadAndReplace = async () => {
    if (selectedFiles.length === 0) {
      alert('Veuillez sélectionner au moins une image');
      return;
    }

    setUploading(true);
    const results = [];

    try {
      for (let i = 0; i < selectedFiles.length; i++) {
        const file = selectedFiles[i];
        const productId = productAssociations[i];
        
        if (!productId) {
          continue;
        }

        // Créer FormData pour l'upload
        const formData = new FormData();
        formData.append('image', file);
        formData.append('product_id', productId);
        formData.append('replace_current', 'true');

        try {
          const response = await axios.post(`${backendUrl}/api/admin/upload-product-image`, formData, {
            headers: {
              'Content-Type': 'multipart/form-data'
            }
          });

          if (response.data.success) {
            results.push({
              filename: file.name,
              product: products.find(p => p.id === productId)?.name || productId,
              status: 'success',
              new_image_url: response.data.image_url
            });
          } else {
            results.push({
              filename: file.name,
              product: products.find(p => p.id === productId)?.name || productId,
              status: 'error',
              error: response.data.message || 'Erreur inconnue'
            });
          }
        } catch (error) {
          results.push({
            filename: file.name,
            product: products.find(p => p.id === productId)?.name || productId,
            status: 'error',
            error: error.response?.data?.detail || error.message
          });
        }
      }

      setUploadResults(results);
    } catch (error) {
      alert('Erreur générale: ' + error.message);
    }

    setUploading(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2 flex items-center">
            📤 UPLOAD IMAGES PRODUITS - PHASE 4
          </h1>
          <p className="text-gray-600">
            Remplacez les images Unsplash par les vraies images du PDF Josmoze
          </p>
        </div>

        {/* Zone d'upload */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-8">
          <h2 className="text-xl font-bold text-gray-800 mb-4">📁 Sélection des Images</h2>
          
          <div 
            className="border-2 border-dashed border-blue-300 rounded-lg p-8 text-center hover:border-blue-500 transition-colors"
            onDrop={handleDrop}
            onDragOver={handleDragOver}
          >
            <div className="mb-4">
              <svg className="w-12 h-12 mx-auto text-blue-500 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M9 19l3 3m0 0l3-3m-3 3V10" />
              </svg>
              <p className="text-lg font-semibold text-gray-700">Glissez vos images ici ou cliquez pour sélectionner</p>
              <p className="text-sm text-gray-500 mt-2">Images du PDF • JPG, PNG, WebP • Max 5MB par image</p>
            </div>
            
            <input
              type="file"
              multiple
              accept="image/*"
              onChange={handleFileSelect}
              className="hidden"
              id="file-input"
            />
            <label 
              htmlFor="file-input"
              className="inline-block px-6 py-3 bg-blue-600 text-white rounded-lg cursor-pointer hover:bg-blue-700 transition-colors"
            >
              📁 Choisir fichiers
            </label>
          </div>

          {selectedFiles.length > 0 && (
            <div className="mt-6">
              <p className="text-sm text-green-600 font-medium">
                ✅ {selectedFiles.length} image{selectedFiles.length > 1 ? 's' : ''} sélectionnée{selectedFiles.length > 1 ? 's' : ''}
              </p>
            </div>
          )}
        </div>

        {/* Association aux produits */}
        {selectedFiles.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <h2 className="text-xl font-bold text-gray-800 mb-4">🔗 Association aux Produits</h2>
            
            <div className="space-y-4">
              {selectedFiles.map((file, index) => (
                <div key={index} className="flex items-center space-x-4 p-4 bg-gray-50 rounded-lg">
                  {/* Prévisualisation image */}
                  <div className="w-20 h-20 bg-gray-200 rounded-lg flex items-center justify-center overflow-hidden">
                    <img
                      src={URL.createObjectURL(file)}
                      alt={`Preview ${index + 1}`}
                      className="w-full h-full object-cover"
                    />
                  </div>
                  
                  {/* Nom fichier */}
                  <div className="flex-1">
                    <p className="font-medium text-gray-800">{file.name}</p>
                    <p className="text-sm text-gray-500">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                  
                  {/* Sélection produit */}
                  <div className="flex-1">
                    <select
                      value={productAssociations[index] || ''}
                      onChange={(e) => updateProductAssociation(index, e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">Sélectionner un produit...</option>
                      {availableProducts.map(product => (
                        <option key={product.id} value={product.id}>
                          {product.name}
                        </option>
                      ))}
                    </select>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Bouton d'action */}
        {selectedFiles.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6 mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-lg font-bold text-gray-800">🚀 Remplacement des Images</h3>
                <p className="text-sm text-gray-600">
                  Les images Unsplash actuelles seront remplacées par vos nouvelles images
                </p>
              </div>
              
              <button
                onClick={handleUploadAndReplace}
                disabled={uploading || Object.keys(productAssociations).length === 0}
                className={`px-8 py-3 rounded-lg font-bold text-lg transition-all ${
                  uploading || Object.keys(productAssociations).length === 0
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-gradient-to-r from-green-500 to-blue-600 text-white hover:from-green-600 hover:to-blue-700 shadow-lg transform hover:scale-105'
                }`}
              >
                {uploading ? '⏳ Upload en cours...' : '🚀 Remplacer les images'}
              </button>
            </div>
          </div>
        )}

        {/* Résultats */}
        {uploadResults.length > 0 && (
          <div className="bg-white rounded-lg shadow-md p-6">
            <h2 className="text-xl font-bold text-gray-800 mb-4">📊 Résultats</h2>
            
            <div className="space-y-3">
              {uploadResults.map((result, index) => (
                <div key={index} className={`p-4 rounded-lg ${
                  result.status === 'success' ? 'bg-green-50 border border-green-200' : 'bg-red-50 border border-red-200'
                }`}>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="font-medium">
                        {result.status === 'success' ? '✅' : '❌'} {result.filename}
                      </p>
                      <p className="text-sm text-gray-600">Produit: {result.product}</p>
                      {result.error && (
                        <p className="text-sm text-red-600 mt-1">Erreur: {result.error}</p>
                      )}
                    </div>
                    
                    {result.new_image_url && (
                      <div className="w-16 h-16 bg-gray-200 rounded-lg overflow-hidden">
                        <img
                          src={result.new_image_url}
                          alt="Nouvelle image"
                          className="w-full h-full object-cover"
                        />
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
            
            <div className="mt-6 text-center">
              <button
                onClick={() => window.location.reload()}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
              >
                🔄 Effectuer un nouvel upload
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AdminUploadImages;