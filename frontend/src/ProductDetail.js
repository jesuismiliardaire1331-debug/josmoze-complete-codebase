import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useApp } from './App';
import axios from 'axios';

const ProductDetail = () => {
  const { productId } = useParams();
  const navigate = useNavigate();
  const { addToCart, formatPrice } = useApp();
  const [product, setProduct] = useState(null);
  const [loading, setLoading] = useState(true);
  const [selectedImage, setSelectedImage] = useState(0);
  const [quantity, setQuantity] = useState(1);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const response = await axios.get(`${backendUrl}/api/products/${productId}`);
        setProduct(response.data);
        setLoading(false);
      } catch (error) {
        console.error('Erreur chargement produit:', error);
        setLoading(false);
      }
    };

    if (productId) {
      fetchProduct();
    }
  }, [productId, backendUrl]);

  const handleAddToCart = () => {
    if (product) {
      addToCart({
        id: product.id,
        name: product.name,
        price: product.price,
        image: product.image,
        quantity: quantity
      });
      
      // Feedback visuel
      alert(`${product.name} ajouté au panier (${quantity} unité${quantity > 1 ? 's' : ''})`);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Chargement du produit...</p>
        </div>
      </div>
    );
  }

  if (!product) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Produit non trouvé</h2>
          <button 
            onClick={() => navigate('/')}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
          >
            Retour à l'accueil
          </button>
        </div>
      </div>
    );
  }

  const images = product.images_gallery && product.images_gallery.length > 0 
    ? product.images_gallery 
    : [product.image];

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Breadcrumb */}
      <nav className="mb-8">
        <div className="flex items-center space-x-2 text-sm">
          <button 
            onClick={() => navigate('/')}
            className="text-blue-600 hover:text-blue-800"
          >
            Accueil
          </button>
          <span className="text-gray-500">/</span>
          <span className="text-gray-900">{product.name}</span>
        </div>
      </nav>

      <div className="grid lg:grid-cols-2 gap-12">
        {/* Galerie d'images */}
        <div>
          <div className="mb-4">
            <img
              src={images[selectedImage]}
              alt={product.name}
              className="w-full h-96 object-cover rounded-lg border"
              onError={(e) => {
                e.target.src = 'https://via.placeholder.com/400x300?text=Image+Non+Disponible';
              }}
            />
          </div>
          
          {images.length > 1 && (
            <div className="flex space-x-2">
              {images.map((image, index) => (
                <button
                  key={index}
                  onClick={() => setSelectedImage(index)}
                  className={`w-20 h-20 rounded border-2 ${
                    selectedImage === index ? 'border-blue-600' : 'border-gray-300'
                  }`}
                >
                  <img
                    src={image}
                    alt={`${product.name} ${index + 1}`}
                    className="w-full h-full object-cover rounded"
                    onError={(e) => {
                      e.target.src = 'https://via.placeholder.com/80x80?text=N/A';
                    }}
                  />
                </button>
              ))}
            </div>
          )}
        </div>

        {/* Informations produit */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-4">{product.name}</h1>
          
          {/* Prix */}
          <div className="mb-6">
            <div className="flex items-center space-x-4">
              <span className="text-3xl font-bold text-blue-600">
                {formatPrice(product.price)}
              </span>
              {product.original_price && (
                <span className="text-xl text-gray-500 line-through">
                  {formatPrice(product.original_price)}
                </span>
              )}
            </div>
            {product.original_price && (
              <div className="text-sm text-green-600 font-medium">
                Économie de {formatPrice(product.original_price - product.price)}
              </div>
            )}
          </div>

          {/* Stock */}
          <div className="mb-6">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mr-2"></div>
              <span className="text-green-600 font-medium">En stock</span>
            </div>
          </div>

          {/* Description */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-3">Description</h3>
            <p className="text-gray-700 leading-relaxed">{product.description}</p>
          </div>

          {/* Spécifications techniques */}
          {product.specifications && Object.keys(product.specifications).length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold mb-3">Spécifications Techniques</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                {Object.entries(product.specifications).map(([key, value]) => (
                  <div key={key} className="flex justify-between py-2 border-b border-gray-200 last:border-b-0">
                    <span className="font-medium text-gray-700">{key}:</span>
                    <span className="text-gray-900">{value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Caractéristiques */}
          {product.features && product.features.length > 0 && (
            <div className="mb-8">
              <h3 className="text-lg font-semibold mb-3">Caractéristiques</h3>
              <ul className="space-y-2">
                {product.features.map((feature, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-blue-600 mr-2">✓</span>
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Ajout au panier */}
          <div className="border-t pt-6">
            <div className="flex items-center space-x-4 mb-4">
              <label className="text-sm font-medium text-gray-700">Quantité:</label>
              <div className="flex items-center">
                <button
                  onClick={() => setQuantity(Math.max(1, quantity - 1))}
                  className="w-8 h-8 rounded-l-md bg-gray-200 flex items-center justify-center hover:bg-gray-300"
                >
                  -
                </button>
                <input
                  type="number"
                  min="1"
                  value={quantity}
                  onChange={(e) => setQuantity(Math.max(1, parseInt(e.target.value) || 1))}
                  className="w-16 h-8 text-center border-t border-b border-gray-200"
                />
                <button
                  onClick={() => setQuantity(quantity + 1)}
                  className="w-8 h-8 rounded-r-md bg-gray-200 flex items-center justify-center hover:bg-gray-300"
                >
                  +
                </button>
              </div>
            </div>

            <div className="flex space-x-4">
              <button
                onClick={handleAddToCart}
                className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
              >
                Ajouter au Panier - {formatPrice(product.price * quantity)}
              </button>
              
              <button
                onClick={() => navigate('/checkout')}
                className="flex-1 bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700 transition-colors"
              >
                Acheter Maintenant
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Informations supplémentaires */}
      <div className="mt-12 grid md:grid-cols-3 gap-8">
        <div className="text-center p-6 bg-blue-50 rounded-lg">
          <div className="text-3xl mb-3">🚚</div>
          <h4 className="font-semibold mb-2">Livraison Gratuite</h4>
          <p className="text-sm text-gray-600">Partout en Europe sous 3-5 jours ouvrés</p>
        </div>
        
        <div className="text-center p-6 bg-green-50 rounded-lg">
          <div className="text-3xl mb-3">🛡️</div>
          <h4 className="font-semibold mb-2">Garantie 2 ans</h4>
          <p className="text-sm text-gray-600">Pièces et main d'œuvre incluses</p>
        </div>
        
        <div className="text-center p-6 bg-yellow-50 rounded-lg">
          <div className="text-3xl mb-3">🔧</div>
          <h4 className="font-semibold mb-2">Installation</h4>
          <p className="text-sm text-gray-600">Support technique gratuit 7j/7</p>
        </div>
      </div>
    </div>
  );
};

export default ProductDetail;