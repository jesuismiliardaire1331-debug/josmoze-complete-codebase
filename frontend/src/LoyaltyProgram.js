import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNotifications } from './NotificationSystem';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

const LoyaltyProgram = ({ customerEmail, isOpen, onClose }) => {
  const [loyaltyStatus, setLoyaltyStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedReward, setSelectedReward] = useState(null);
  const [redeeming, setRedeeming] = useState(false);
  const notifications = useNotifications();

  useEffect(() => {
    if (isOpen && customerEmail) {
      fetchLoyaltyStatus();
    }
  }, [isOpen, customerEmail]);

  const fetchLoyaltyStatus = async () => {
    try {
      setLoading(true);
      const response = await axios.get(
        `${BACKEND_URL}/api/loyalty/status/${encodeURIComponent(customerEmail)}`
      );

      if (response.data.success) {
        setLoyaltyStatus(response.data);
      } else {
        setError('Impossible de charger votre statut fidélité');
      }
    } catch (err) {
      console.error('Loyalty status fetch error:', err);
      setError('Erreur lors du chargement du programme fidélité');
    } finally {
      setLoading(false);
    }
  };

  const handleRedeemReward = async (reward) => {
    if (!reward || redeeming) return;

    try {
      setRedeeming(true);
      
      const response = await axios.post(
        `${BACKEND_URL}/api/loyalty/redeem`,
        {
          customer_id: customerEmail,
          reward_id: reward.id
        }
      );

      if (response.data.success) {
        notifications.success(
          '🎉 Récompense Échangée',
          `Code: ${response.data.reward_code}`
        );
        
        // Refresh status
        await fetchLoyaltyStatus();
        setSelectedReward(null);
      } else {
        notifications.error(
          '❌ Échange Échoué',
          response.data.error || 'Impossible d\'échanger cette récompense'
        );
      }
    } catch (err) {
      console.error('Redeem reward error:', err);
      notifications.error(
        '❌ Erreur',
        'Erreur lors de l\'échange de la récompense'
      );
    } finally {
      setRedeeming(false);
    }
  };

  const getTierColor = (tier) => {
    const colors = {
      bronze: 'from-yellow-600 to-yellow-800',
      silver: 'from-gray-400 to-gray-600',
      gold: 'from-yellow-400 to-yellow-600',
      platinum: 'from-purple-400 to-purple-600'
    };
    return colors[tier] || colors.bronze;
  };

  const getTierIcon = (tier) => {
    const icons = {
      bronze: '🥉',
      silver: '🥈', 
      gold: '🥇',
      platinum: '💎'
    };
    return icons[tier] || icons.bronze;
  };

  const getRewardTypeIcon = (type) => {
    const icons = {
      discount_percentage: '🏷️',
      discount_amount: '💰',
      free_shipping: '🚚',
      free_product: '🎁',
      early_access: '⭐'
    };
    return icons[type] || '🎯';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-FR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-4xl w-full max-h-[90vh] overflow-auto">
        
        {/* Header */}
        <div className="sticky top-0 bg-white border-b border-gray-200 p-6 flex justify-between items-center">
          <div>
            <h2 className="text-2xl font-bold text-gray-900">💎 Programme Fidélité Josmose</h2>
            <p className="text-gray-600">Gagnez des points à chaque achat et débloquez des récompenses exclusives</p>
          </div>
          <button 
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700 text-2xl font-bold"
          >
            ×
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {loading && (
            <div className="text-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
              <p className="text-gray-600">Chargement de votre statut fidélité...</p>
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
              <div className="text-red-600 text-4xl mb-4">😕</div>
              <h3 className="text-lg font-semibold text-red-900 mb-2">Oups !</h3>
              <p className="text-red-700">{error}</p>
              <button 
                onClick={fetchLoyaltyStatus}
                className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
              >
                Réessayer
              </button>
            </div>
          )}

          {loyaltyStatus && loyaltyStatus.success && (
            <div className="space-y-8">
              
              {/* Customer Status Card */}
              <div className={`bg-gradient-to-r ${getTierColor(loyaltyStatus.customer.tier)} rounded-2xl p-6 text-white`}>
                <div className="flex items-center justify-between mb-6">
                  <div>
                    <div className="flex items-center space-x-3 mb-2">
                      <span className="text-3xl">{getTierIcon(loyaltyStatus.customer.tier)}</span>
                      <h3 className="text-2xl font-bold capitalize">
                        Membre {loyaltyStatus.customer.tier}
                      </h3>
                    </div>
                    <p className="text-lg opacity-90">{loyaltyStatus.customer.name}</p>
                  </div>
                  <div className="text-right">
                    <div className="text-3xl font-bold">{loyaltyStatus.customer.points}</div>
                    <div className="text-sm opacity-90">Points disponibles</div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="bg-white bg-opacity-20 rounded-lg p-4">
                    <div className="text-2xl font-bold">{loyaltyStatus.customer.orders_count}</div>
                    <div className="text-sm opacity-90">Commandes</div>
                  </div>
                  <div className="bg-white bg-opacity-20 rounded-lg p-4">
                    <div className="text-2xl font-bold">{loyaltyStatus.customer.total_spent?.toFixed(2)}€</div>
                    <div className="text-sm opacity-90">Dépensé au total</div>
                  </div>
                  <div className="bg-white bg-opacity-20 rounded-lg p-4">
                    <div className="text-2xl font-bold">{loyaltyStatus.statistics.rewards_redeemed}</div>
                    <div className="text-sm opacity-90">Récompenses échangées</div>
                  </div>
                </div>

                {/* Progress to next tier */}
                {loyaltyStatus.tier_info.next_tier && (
                  <div className="mt-6">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-sm opacity-90">Progression vers {loyaltyStatus.tier_info.next_tier}</span>
                      <span className="text-sm opacity-90">
                        {loyaltyStatus.tier_info.points_to_next_tier} points restants
                      </span>
                    </div>
                    <div className="w-full bg-white bg-opacity-20 rounded-full h-2">
                      <div 
                        className="bg-white h-2 rounded-full transition-all duration-300"
                        style={{
                          width: `${Math.max(10, 100 - (loyaltyStatus.tier_info.points_to_next_tier / loyaltyStatus.customer.points) * 100)}%`
                        }}
                      ></div>
                    </div>
                  </div>
                )}
              </div>

              {/* Tier Benefits */}
              <div className="bg-white border border-gray-200 rounded-xl p-6">
                <h4 className="text-xl font-bold text-gray-900 mb-4">
                  🎯 Vos Avantages Niveau {loyaltyStatus.customer.tier.charAt(0).toUpperCase() + loyaltyStatus.customer.tier.slice(1)}
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {loyaltyStatus.tier_info.tier_benefits.map((benefit, index) => (
                    <div key={index} className="flex items-start space-x-3 p-3 bg-blue-50 rounded-lg">
                      <span className="text-blue-600 mt-1">✓</span>
                      <span className="text-gray-700">{benefit}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Available Rewards */}
              <div className="bg-white border border-gray-200 rounded-xl p-6">
                <h4 className="text-xl font-bold text-gray-900 mb-4">🎁 Récompenses Disponibles</h4>
                
                {loyaltyStatus.available_rewards.length === 0 ? (
                  <div className="text-center py-8">
                    <div className="text-gray-400 text-4xl mb-2">🎯</div>
                    <p className="text-gray-600">
                      Continuez à gagner des points pour débloquer des récompenses !
                    </p>
                  </div>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {loyaltyStatus.available_rewards.map((reward) => (
                      <div 
                        key={reward.id}
                        className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow cursor-pointer"
                        onClick={() => setSelectedReward(reward)}
                      >
                        <div className="flex items-start justify-between mb-3">
                          <span className="text-2xl">{getRewardTypeIcon(reward.reward_type)}</span>
                          <div className="text-right">
                            <div className="text-lg font-bold text-blue-600">{reward.points_cost}</div>
                            <div className="text-xs text-gray-500">points</div>
                          </div>
                        </div>
                        
                        <h5 className="font-semibold text-gray-900 mb-2">{reward.name}</h5>
                        <p className="text-sm text-gray-600 mb-3">{reward.description}</p>
                        
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            handleRedeemReward(reward);
                          }}
                          disabled={redeeming || loyaltyStatus.customer.points < reward.points_cost}
                          className={`w-full py-2 px-4 rounded-lg text-sm font-medium transition-colors ${
                            loyaltyStatus.customer.points >= reward.points_cost && !redeeming
                              ? 'bg-blue-600 text-white hover:bg-blue-700'
                              : 'bg-gray-200 text-gray-500 cursor-not-allowed'
                          }`}
                        >
                          {redeeming ? 'Échange...' : 'Échanger'}
                        </button>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Recent Transactions */}
              {loyaltyStatus.recent_transactions.length > 0 && (
                <div className="bg-white border border-gray-200 rounded-xl p-6">
                  <h4 className="text-xl font-bold text-gray-900 mb-4">📈 Activité Récente</h4>
                  <div className="space-y-3">
                    {loyaltyStatus.recent_transactions.slice(0, 5).map((transaction, index) => (
                      <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                        <div>
                          <p className="text-sm font-medium text-gray-900">{transaction.description}</p>
                          <p className="text-xs text-gray-500">
                            {formatDate(transaction.created_at)}
                          </p>
                        </div>
                        <div className={`font-bold ${
                          transaction.points_change > 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {transaction.points_change > 0 ? '+' : ''}{transaction.points_change} pts
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Member Since */}
              <div className="text-center text-gray-500 text-sm">
                Membre depuis le {formatDate(loyaltyStatus.statistics.member_since)} • 
                {loyaltyStatus.statistics.total_points_earned} points gagnés au total
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Mini component for loyalty points display in header/cart
export const LoyaltyPointsDisplay = ({ customerEmail }) => {
  const [points, setPoints] = useState(0);
  const [tier, setTier] = useState('bronze');
  const [showProgram, setShowProgram] = useState(false);

  useEffect(() => {
    if (customerEmail) {
      fetchQuickStatus();
    }
  }, [customerEmail]);

  const fetchQuickStatus = async () => {
    try {
      const response = await axios.get(
        `${BACKEND_URL}/api/loyalty/status/${encodeURIComponent(customerEmail)}`
      );

      if (response.data.success) {
        setPoints(response.data.customer.points);
        setTier(response.data.customer.tier);
      }
    } catch (err) {
      console.error('Quick loyalty status error:', err);
    }
  };

  if (!customerEmail) return null;

  return (
    <>
      <button
        onClick={() => setShowProgram(true)}
        className="flex items-center space-x-2 px-3 py-2 bg-gradient-to-r from-yellow-400 to-yellow-600 text-white rounded-lg hover:from-yellow-500 hover:to-yellow-700 transition-all"
      >
        <span>{getTierIcon(tier)}</span>
        <span className="font-medium">{points} pts</span>
      </button>

      <LoyaltyProgram
        customerEmail={customerEmail}
        isOpen={showProgram}
        onClose={() => setShowProgram(false)}
      />
    </>
  );
};

const getTierIcon = (tier) => {
  const icons = {
    bronze: '🥉',
    silver: '🥈', 
    gold: '🥇',
    platinum: '💎'
  };
  return icons[tier] || icons.bronze;
};

export default LoyaltyProgram;