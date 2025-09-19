import React, { useState, useEffect } from 'react';
import axios from 'axios';

const AdminUpload = () => {
  const [selectedFile, setSelectedFile] = useState(null);
  const [productId, setProductId] = useState('');
  const [mediaType, setMediaType] = useState('image');
  const [description, setDescription] = useState('');
  const [uploading, setUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState(null);
  const [mediaLibrary, setMediaLibrary] = useState([]);
  const [loading, setLoading] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || window.location.origin;

  useEffect(() => {
    loadMediaLibrary();
  }, []);

  const loadMediaLibrary = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${backendUrl}/api/admin/media/library`);
      if (response.data.success) {
        setMediaLibrary(response.data.media_list);
      }
    } catch (error) {
      console.error('Erreur chargement bibliothèque:', error);
    }
    setLoading(false);
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedFile(file);
      setUploadResult(null);
    }
  };

  const handleUpload = async () => {
    if (!selectedFile) {
      alert('Veuillez sélectionner un fichier');
      return;
    }

    setUploading(true);
    setUploadResult(null);

    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      formData.append('media_type', mediaType);
      if (productId) formData.append('product_id', productId);
      if (description) formData.append('description', description);

      const response = await axios.post(
        `${backendUrl}/api/admin/upload/media`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );

      if (response.data.success) {
        setUploadResult({
          success: true,
          message: response.data.message,
          data: response.data
        });
        
        // Réinitialiser le formulaire
        setSelectedFile(null);
        setProductId('');
        setDescription('');
        document.getElementById('fileInput').value = '';
        
        // Recharger la bibliothèque
        await loadMediaLibrary();
      }
    } catch (error) {
      setUploadResult({
        success: false,
        message: error.response?.data?.detail || 'Erreur lors de l\'upload'
      });
    }

    setUploading(false);
  };

  const handleDeleteMedia = async (mediaId) => {
    if (!window.confirm('Êtes-vous sûr de vouloir supprimer ce média ?')) {
      return;
    }

    try {
      await axios.delete(`${backendUrl}/api/admin/media/${mediaId}`);
      await loadMediaLibrary();
    } catch (error) {
      alert('Erreur lors de la suppression');
    }
  };

  const getFileIcon = (mediaType, extension) => {
    if (mediaType === 'image') return '🖼️';
    if (mediaType === 'video') return '🎥';
    return '📄';
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="max-w-6xl mx-auto p-6 bg-white">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          🔧 Administration - Gestionnaire d'Upload
        </h1>
        <p className="text-gray-600">
          Interface d'administration pour l'upload manuel d'images et vidéos produits
        </p>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        {/* Formulaire d'upload */}
        <div className="bg-gray-50 p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">📤 Upload de Média</h2>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Type de média
              </label>
              <select
                value={mediaType}
                onChange={(e) => setMediaType(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="image">Image (JPG, PNG, WebP)</option>
                <option value="video">Vidéo (MP4, WebM, MOV)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Fichier
              </label>
              <input
                id="fileInput"
                type="file"
                onChange={handleFileSelect}
                accept={mediaType === 'image' ? 'image/*' : 'video/*'}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              {selectedFile && (
                <p className="mt-2 text-sm text-gray-600">
                  Fichier sélectionné: {selectedFile.name} ({formatFileSize(selectedFile.size)})
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                ID Produit (optionnel)
              </label>
              <input
                type="text"
                value={productId}
                onChange={(e) => setProductId(e.target.value)}
                placeholder="osmoseur-essentiel"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description (optionnel)
              </label>
              <textarea
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Description du média..."
                rows="3"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
            </div>

            <button
              onClick={handleUpload}
              disabled={!selectedFile || uploading}
              className={`w-full py-3 px-4 rounded-lg font-semibold transition-colors ${
                !selectedFile || uploading
                  ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {uploading ? '⏳ Upload en cours...' : '📤 Uploader le fichier'}
            </button>
          </div>

          {uploadResult && (
            <div className={`mt-4 p-4 rounded-lg ${
              uploadResult.success 
                ? 'bg-green-100 border border-green-300 text-green-800'
                : 'bg-red-100 border border-red-300 text-red-800'
            }`}>
              <p className="font-medium">
                {uploadResult.success ? '✅ Succès!' : '❌ Erreur!'}
              </p>
              <p className="text-sm">{uploadResult.message}</p>
              {uploadResult.success && uploadResult.data && (
                <div className="mt-2 text-xs">
                  <p>URL: {uploadResult.data.public_url}</p>
                  <p>Taille: {formatFileSize(uploadResult.data.file_size)}</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Aperçu bibliothèque */}
        <div className="bg-gray-50 p-6 rounded-lg">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">📚 Bibliothèque de Médias</h2>
            <button
              onClick={loadMediaLibrary}
              disabled={loading}
              className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
            >
              {loading ? '⏳' : '🔄'} Actualiser
            </button>
          </div>

          <div className="space-y-3 max-h-96 overflow-y-auto">
            {mediaLibrary.length === 0 ? (
              <p className="text-gray-500 text-center py-8">
                Aucun média dans la bibliothèque
              </p>
            ) : (
              mediaLibrary.map((media) => (
                <div key={media.id} className="bg-white p-4 rounded-lg shadow-sm border">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-2">
                        <span className="text-xl">
                          {getFileIcon(media.media_type, media.file_extension)}
                        </span>
                        <span className="font-medium text-gray-900">
                          {media.original_name}
                        </span>
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          media.media_type === 'image' 
                            ? 'bg-green-100 text-green-800'
                            : 'bg-blue-100 text-blue-800'
                        }`}>
                          {media.media_type}
                        </span>
                      </div>
                      
                      <div className="text-sm text-gray-600 space-y-1">
                        <p>Taille: {formatFileSize(media.file_size)}</p>
                        <p>URL: <code className="bg-gray-100 px-1 rounded text-xs">{media.public_url}</code></p>
                        {media.product_id && <p>Produit: {media.product_id}</p>}
                        {media.description && <p>Description: {media.description}</p>}
                      </div>
                    </div>
                    
                    <button
                      onClick={() => handleDeleteMedia(media.id)}
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
        </div>
      </div>
    </div>
  );
};

export default AdminUpload;