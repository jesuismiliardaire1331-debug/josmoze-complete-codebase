import React, { useState, useEffect } from 'react';
import { useApp } from './App';
import { useAuth } from './UserAuth';
import axios from 'axios';

const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const CheckoutWithPromo = () => {
  const { cart, formatPrice, clearCart } = useApp();
  const { user, isAuthenticated } = useAuth();
  
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [step, setStep] = useState(1); // 1: panier, 2: infos, 3: paiement
  
  // Promotion state
  const [promoCode, setPromoCode] = useState('');
  const [promoValidation, setPromoValidation] = useState(null);
  const [promoLoading, setPromoLoading] = useState(false);
  
  // Référence state
  const [referralCode, setReferralCode] = useState('');
  const [referralValidation, setReferralValidation] = useState(null);
  const [referralLoading, setReferralLoading] = useState(false);
  
  // Order calculation
  const [orderSummary, setOrderSummary] = useState({
    subtotal: 0,
    promoDiscount: 0,
    referralDiscount: 0,
    shippingCost: 0,
    total: 0
  });
  
  // Customer info
  const [customerInfo, setCustomerInfo] = useState({
    email: user?.email || '',
    first_name: user?.first_name || '',
    last_name: user?.last_name || '',
    phone: user?.phone || '',
    address: {
      street: '',
      city: '',
      postal_code: '',
      country: 'France'
    },
    customer_type: user?.customer_type || 'B2C'
  });

  // Calculer totaux
  useEffect(() => {
    calculateOrder();
  }, [cart, promoValidation, referralValidation]);

  const calculateOrder = () => {
    const subtotal = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    let promoDiscount = promoValidation?.valid ? promoValidation.discount_amount : 0;
    let referralDiscount = referralValidation?.valid ? referralValidation.discount_amount : 0;
    const shippingCost = subtotal >= 300 ? 0 : 29.90; // Livraison gratuite à partir de 300€
    
    // Appliquer la meilleure réduction (pas les deux)
    const bestDiscount = Math.max(promoDiscount, referralDiscount);
    if (bestDiscount === promoDiscount) {
      referralDiscount = 0;
    } else {
      promoDiscount = 0;
    }
    
    const total = Math.max(0, subtotal - promoDiscount - referralDiscount + shippingCost);
    
    setOrderSummary({
      subtotal,
      promoDiscount,
      referralDiscount,
      shippingCost,
      total
    });
  };

  const validatePromoCode = async () => {
    if (!promoCode.trim()) return;
    
    setPromoLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/api/promotions/validate`, {
        code: promoCode.trim(),
        user_email: customerInfo.email || 'guest@josmoze.com',
        order_amount: orderSummary.subtotal,
        customer_type: customerInfo.customer_type
      });

      if (response.data.valid) {
        setPromoValidation(response.data);
        setMessage('✅ Code promotionnel appliqué !');
        // Reset referral si promo appliquée
        if (referralValidation) {
          setReferralCode('');
          setReferralValidation(null);
        }
      } else {
        setPromoValidation(null);
        setMessage(`❌ ${response.data.error}`);
      }
    } catch (error) {
      console.error('Error validating promo:', error);
      setMessage('❌ Erreur lors de la validation du code');
    } finally {
      setPromoLoading(false);
    }
  };

  const validateReferralCode = async () => {
    if (!referralCode.trim()) return;
    
    setReferralLoading(true);
    try {
      const response = await axios.post(`${API_BASE}/api/referrals/validate`, {
        code: referralCode.trim(),
        referee_email: customerInfo.email || 'guest@josmoze.com'
      });

      if (response.data.valid) {
        // Calculer réduction parrainage
        const discountAmount = orderSummary.subtotal * (response.data.referral.discount_percent / 100);
        setReferralValidation({
          ...response.data,
          discount_amount: discountAmount
        });
        setMessage(`✅ Code parrainage appliqué ! ${response.data.referral.discount_percent}% de réduction`);
        // Reset promo si parrainage appliqué
        if (promoValidation) {
          setPromoCode('');
          setPromoValidation(null);
        }
      } else {
        setReferralValidation(null);
        setMessage(`❌ ${response.data.error}`);
      }
    } catch (error) {
      console.error('Error validating referral:', error);
      setMessage('❌ Erreur lors de la validation du code parrainage');
    } finally {
      setReferralLoading(false);
    }
  };

  const removePromotion = () => {
    setPromoCode('');
    setPromoValidation(null);
    setMessage('Code promotionnel retiré');
  };

  const removeReferral = () => {
    setReferralCode('');
    setReferralValidation(null);
    setMessage('Code parrainage retiré');
  };

  const processOrder = async () => {
    setLoading(true);
    try {
      // Créer commande
      const orderData = {
        items: cart.map(item => ({
          product_id: item.id,
          name: item.name,
          price: item.price,
          quantity: item.quantity,
          image: item.image
        })),
        subtotal: orderSummary.subtotal,
        discount_amount: orderSummary.promoDiscount + orderSummary.referralDiscount,
        shipping_cost: orderSummary.shippingCost,
        total: orderSummary.total,
        promotion_code: promoValidation?.promotion?.code || null,
        referral_code: referralValidation?.referral?.referrer_code || null,
        shipping_address: customerInfo.address,
        billing_address: customerInfo.address,
        payment_method: 'card',
        payment_status: 'pending',
        status: 'pending'
      };

      if (isAuthenticated) {
        // Commande avec compte
        const response = await axios.post(`${API_BASE}/api/orders/create`, orderData, {
          headers: { Authorization: `Bearer ${localStorage.getItem('user_token')}` }
        });
        
        if (response.data.success) {
          setMessage('✅ Commande créée avec succès !');
          handleOrderSuccess(response.data.order_id);
        }
      } else {
        // Commande invité
        orderData.user_email = customerInfo.email;
        const response = await axios.post(`${API_BASE}/api/orders/create`, orderData);
        
        if (response.data.success) {
          setMessage('✅ Commande créée avec succès !');
          handleOrderSuccess(response.data.order_id);
        }
      }
      
    } catch (error) {
      console.error('Error processing order:', error);
      setMessage('❌ Erreur lors de la création de la commande');
    } finally {
      setLoading(false);
    }
  };

  const handleOrderSuccess = (orderId) => {
    // Appliquer les promotions définitivement
    if (promoValidation?.valid) {
      axios.post(`${API_BASE}/api/promotions/apply`, {
        code: promoValidation.promotion.code,
        user_email: customerInfo.email,
        order_amount: orderSummary.subtotal,
        order_id: orderId
      }).catch(console.error);
    }
    
    if (referralValidation?.valid) {
      axios.post(`${API_BASE}/api/referrals/apply`, {
        code: referralValidation.referral.referrer_code,
        referee_email: customerInfo.email,
        order_amount: orderSummary.subtotal,
        order_id: orderId
      }).catch(console.error);
    }
    
    clearCart();
    setStep(4); // Confirmation
  };

  if (cart.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-2xl mx-auto px-4 text-center">
          <h2 className="text-2xl font-bold mb-4">🛒 Panier vide</h2>
          <p className="text-gray-600 mb-6">Votre panier est vide. Découvrez nos produits !</p>
          <button
            onClick={() => window.location.href = '/'}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
          >
            Découvrir nos osmoseurs
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-4">
            <div className={`flex items-center ${step >= 1 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                step >= 1 ? 'bg-blue-600 text-white' : 'bg-gray-300'
              }`}>1</div>
              <span className="ml-2 font-medium">Panier</span>
            </div>
            <div className={`flex items-center ${step >= 2 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                step >= 2 ? 'bg-blue-600 text-white' : 'bg-gray-300'
              }`}>2</div>
              <span className="ml-2 font-medium">Informations</span>
            </div>
            <div className={`flex items-center ${step >= 3 ? 'text-blue-600' : 'text-gray-400'}`}>
              <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${
                step >= 3 ? 'bg-blue-600 text-white' : 'bg-gray-300'
              }`}>3</div>
              <span className="ml-2 font-medium">Paiement</span>
            </div>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(step / 3) * 100}%` }}
            ></div>
          </div>
        </div>

        {/* Messages */}
        {message && (
          <div className={`p-4 rounded-lg mb-6 ${
            message.includes('✅') ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {message}
            <button 
              onClick={() => setMessage('')}
              className="float-right text-lg font-bold ml-4"
            >
              ×
            </button>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Contenu principal */}
          <div className="lg:col-span-2">
            {step === 1 && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-semibold mb-6">🛒 Votre Panier</h2>
                
                <div className="space-y-4 mb-6">
                  {cart.map((item) => (
                    <div key={item.id} className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg">
                      <img
                        src={item.image}
                        alt={item.name}
                        className="w-20 h-20 object-cover rounded-lg"
                      />
                      <div className="flex-1">
                        <h3 className="font-medium text-gray-800">{item.name}</h3>
                        <p className="text-gray-600">Quantité: {item.quantity}</p>
                      </div>
                      <div className="text-right">
                        <div className="font-semibold text-gray-800">
                          {formatPrice(item.price * item.quantity)}
                        </div>
                        <div className="text-sm text-gray-500">
                          {formatPrice(item.price)} / unité
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Codes promotionnels */}
                <div className="border-t pt-6 space-y-4">
                  <h3 className="font-medium text-gray-800">🎁 Codes de réduction</h3>
                  
                  {/* Code promo */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Code promotionnel
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={promoCode}
                        onChange={(e) => setPromoCode(e.target.value.toUpperCase())}
                        className="flex-1 p-3 border border-gray-300 rounded-lg"
                        placeholder="Ex: BIENVENUE10"
                        disabled={!!referralValidation}
                      />
                      <button
                        onClick={validatePromoCode}
                        disabled={promoLoading || !promoCode.trim() || !!referralValidation}
                        className="bg-blue-600 text-white px-4 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50"
                      >
                        {promoLoading ? '...' : 'Appliquer'}
                      </button>
                    </div>
                    {promoValidation?.valid && (
                      <div className="mt-2 flex items-center justify-between bg-green-50 p-2 rounded">
                        <span className="text-green-800 text-sm">
                          ✅ {promoValidation.promotion.description} - {formatPrice(promoValidation.discount_amount)}
                        </span>
                        <button
                          onClick={removePromotion}
                          className="text-red-600 text-sm hover:text-red-800"
                        >
                          Retirer
                        </button>
                      </div>
                    )}
                  </div>

                  {/* Code parrainage */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Code de parrainage
                    </label>
                    <div className="flex space-x-2">
                      <input
                        type="text"
                        value={referralCode}
                        onChange={(e) => setReferralCode(e.target.value.toUpperCase())}
                        className="flex-1 p-3 border border-gray-300 rounded-lg"
                        placeholder="Ex: JEAN1234"
                        disabled={!!promoValidation}
                      />
                      <button
                        onClick={validateReferralCode}
                        disabled={referralLoading || !referralCode.trim() || !!promoValidation}
                        className="bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 disabled:opacity-50"
                      >
                        {referralLoading ? '...' : 'Appliquer'}
                      </button>
                    </div>
                    {referralValidation?.valid && (
                      <div className="mt-2 flex items-center justify-between bg-green-50 p-2 rounded">
                        <span className="text-green-800 text-sm">
                          ✅ Parrainage: {referralValidation.referral.discount_percent}% - {formatPrice(referralValidation.discount_amount)}
                        </span>
                        <button
                          onClick={removeReferral}
                          className="text-red-600 text-sm hover:text-red-800"
                        >
                          Retirer
                        </button>
                      </div>
                    )}
                  </div>
                  
                  {(promoValidation || referralValidation) && (
                    <p className="text-xs text-gray-500">
                      ℹ️ Un seul code de réduction peut être appliqué par commande
                    </p>
                  )}
                </div>

                <div className="mt-6">
                  <button
                    onClick={() => setStep(2)}
                    className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-medium"
                  >
                    Continuer vers les informations
                  </button>
                </div>
              </div>
            )}

            {step === 2 && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-semibold mb-6">📋 Informations de livraison</h2>
                
                <form className="space-y-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Prénom *
                      </label>
                      <input
                        type="text"
                        value={customerInfo.first_name}
                        onChange={(e) => setCustomerInfo({...customerInfo, first_name: e.target.value})}
                        className="w-full p-3 border border-gray-300 rounded-lg"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Nom *
                      </label>
                      <input
                        type="text"
                        value={customerInfo.last_name}
                        onChange={(e) => setCustomerInfo({...customerInfo, last_name: e.target.value})}
                        className="w-full p-3 border border-gray-300 rounded-lg"
                        required
                      />
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email *
                    </label>
                    <input
                      type="email"
                      value={customerInfo.email}
                      onChange={(e) => setCustomerInfo({...customerInfo, email: e.target.value})}
                      className="w-full p-3 border border-gray-300 rounded-lg"
                      required
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Téléphone
                    </label>
                    <input
                      type="tel"
                      value={customerInfo.phone}
                      onChange={(e) => setCustomerInfo({...customerInfo, phone: e.target.value})}
                      className="w-full p-3 border border-gray-300 rounded-lg"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Adresse *
                    </label>
                    <input
                      type="text"
                      value={customerInfo.address.street}
                      onChange={(e) => setCustomerInfo({
                        ...customerInfo, 
                        address: {...customerInfo.address, street: e.target.value}
                      })}
                      className="w-full p-3 border border-gray-300 rounded-lg"
                      placeholder="123 rue de la Paix"
                      required
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Ville *
                      </label>
                      <input
                        type="text"
                        value={customerInfo.address.city}
                        onChange={(e) => setCustomerInfo({
                          ...customerInfo, 
                          address: {...customerInfo.address, city: e.target.value}
                        })}
                        className="w-full p-3 border border-gray-300 rounded-lg"
                        required
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Code postal *
                      </label>
                      <input
                        type="text"
                        value={customerInfo.address.postal_code}
                        onChange={(e) => setCustomerInfo({
                          ...customerInfo, 
                          address: {...customerInfo.address, postal_code: e.target.value}
                        })}
                        className="w-full p-3 border border-gray-300 rounded-lg"
                        required
                      />
                    </div>
                  </div>
                </form>

                <div className="mt-6 flex space-x-4">
                  <button
                    onClick={() => setStep(1)}
                    className="bg-gray-300 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-400"
                  >
                    Retour
                  </button>
                  <button
                    onClick={() => setStep(3)}
                    className="flex-1 bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 font-medium"
                  >
                    Continuer vers le paiement
                  </button>
                </div>
              </div>
            )}

            {step === 3 && (
              <div className="bg-white rounded-lg shadow-sm p-6">
                <h2 className="text-xl font-semibold mb-6">💳 Paiement</h2>
                
                <div className="bg-blue-50 p-4 rounded-lg mb-6">
                  <p className="text-blue-800 text-sm">
                    ℹ️ Pour cette démonstration, le paiement est simulé. 
                    En production, ici s'intégrerait Stripe ou un autre processeur de paiement.
                  </p>
                </div>

                <div className="space-y-4 mb-6">
                  <div className="border border-gray-300 rounded-lg p-4">
                    <div className="flex items-center mb-2">
                      <input type="radio" id="card" name="payment" defaultChecked className="mr-2" />
                      <label htmlFor="card" className="font-medium">💳 Carte bancaire</label>
                    </div>
                    <div className="text-sm text-gray-600">
                      Paiement sécurisé par carte bancaire
                    </div>
                  </div>
                </div>

                <div className="mt-6 flex space-x-4">
                  <button
                    onClick={() => setStep(2)}
                    className="bg-gray-300 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-400"
                  >
                    Retour
                  </button>
                  <button
                    onClick={processOrder}
                    disabled={loading}
                    className="flex-1 bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 font-medium disabled:opacity-50"
                  >
                    {loading ? 'Traitement...' : `Finaliser la commande - ${formatPrice(orderSummary.total)}`}
                  </button>
                </div>
              </div>
            )}

            {step === 4 && (
              <div className="bg-white rounded-lg shadow-sm p-6 text-center">
                <div className="text-6xl mb-4">🎉</div>
                <h2 className="text-2xl font-bold text-green-600 mb-4">Commande confirmée !</h2>
                <p className="text-gray-600 mb-6">
                  Merci pour votre commande ! Vous recevrez un email de confirmation sous peu.
                </p>
                <button
                  onClick={() => window.location.href = '/'}
                  className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700"
                >
                  Retour à l'accueil
                </button>
              </div>
            )}
          </div>

          {/* Résumé commande */}
          <div className="lg:col-span-1">
            <div className="bg-white rounded-lg shadow-sm p-6 sticky top-4">
              <h3 className="text-lg font-semibold mb-4">📋 Résumé de la commande</h3>
              
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Sous-total:</span>
                  <span>{formatPrice(orderSummary.subtotal)}</span>
                </div>
                
                {orderSummary.promoDiscount > 0 && (
                  <div className="flex justify-between text-green-600">
                    <span>Promotion:</span>
                    <span>-{formatPrice(orderSummary.promoDiscount)}</span>
                  </div>
                )}
                
                {orderSummary.referralDiscount > 0 && (
                  <div className="flex justify-between text-green-600">
                    <span>Parrainage:</span>
                    <span>-{formatPrice(orderSummary.referralDiscount)}</span>
                  </div>
                )}
                
                <div className="flex justify-between">
                  <span>Livraison:</span>
                  <span>
                    {orderSummary.shippingCost === 0 ? 'Gratuite' : formatPrice(orderSummary.shippingCost)}
                  </span>
                </div>
                
                <hr className="my-2" />
                
                <div className="flex justify-between font-semibold text-lg">
                  <span>Total:</span>
                  <span>{formatPrice(orderSummary.total)}</span>
                </div>
              </div>
              
              {orderSummary.subtotal >= 300 && (
                <div className="mt-4 bg-green-50 p-3 rounded-lg">
                  <p className="text-green-800 text-sm">
                    🚚 Livraison gratuite incluse !
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CheckoutWithPromo;