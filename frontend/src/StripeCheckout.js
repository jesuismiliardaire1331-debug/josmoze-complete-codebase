import React, { useState } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import {
  Elements,
  CardElement,
  useStripe,
  useElements
} from '@stripe/react-stripe-js';

// Clé publique Stripe TEST (non sensible)
const stripePromise = loadStripe('pk_test_51N123456789abcdefghijklmnopqrstuvwxyz123456789abcdefghijklmnopqr');

const CheckoutForm = ({ total, onSuccess, onError }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [processing, setProcessing] = useState(false);
  const [succeeded, setSucceeded] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();

    if (!stripe || !elements) {
      return;
    }

    setProcessing(true);

    const cardElement = elements.getElement(CardElement);

    // Créer un token de paiement (mode test)
    const { error, token } = await stripe.createToken(cardElement);

    if (error) {
      console.error('Erreur Stripe:', error);
      onError(error.message);
      setProcessing(false);
    } else {
      console.log('Token Stripe créé:', token);
      
      // Simuler un paiement réussi en mode test
      setTimeout(() => {
        setSucceeded(true);
        setProcessing(false);
        onSuccess({
          paymentMethod: 'stripe',
          token: token.id,
          amount: total,
          status: 'succeeded'
        });
      }, 2000);
    }
  };

  if (succeeded) {
    return (
      <div className="text-center p-6 bg-green-50 rounded-lg">
        <div className="text-4xl mb-4">✅</div>
        <h3 className="text-xl font-bold text-green-800 mb-2">Paiement Réussi !</h3>
        <p className="text-green-600">Votre commande de {total.toFixed(2)}€ a été traitée avec succès.</p>
        <p className="text-sm text-gray-600 mt-2">Mode test - Aucun paiement réel effectué</p>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="bg-white p-4 rounded-lg border">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          Informations de Carte (Mode Test)
        </label>
        <CardElement
          options={{
            style: {
              base: {
                fontSize: '16px',
                color: '#424770',
                '::placeholder': {
                  color: '#aab7c4',
                },
              },
              invalid: {
                color: '#9e2146',
              },
            },
          }}
        />
        <div className="mt-2 text-xs text-gray-500">
          <p>🧪 <strong>Mode Test</strong> - Utilisez une carte test :</p>
          <p>• 4242 4242 4242 4242 (Visa)</p>
          <p>• Date: n'importe quelle date future</p>
          <p>• CVC: n'importe quel code 3 chiffres</p>
        </div>
      </div>

      <button
        type="submit"
        disabled={!stripe || processing}
        className={`w-full py-3 px-4 rounded-lg font-semibold text-white transition-colors ${
          processing
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700'
        }`}
      >
        {processing ? (
          <div className="flex items-center justify-center">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
            Traitement...
          </div>
        ) : (
          `Payer ${total.toFixed(2)}€ (Mode Test)`
        )}
      </button>
    </form>
  );
};

const StripeCheckout = ({ total, onSuccess, onError }) => {
  return (
    <Elements stripe={stripePromise}>
      <div className="max-w-md mx-auto">
        <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-center">
            <span className="text-yellow-600 mr-2">⚠️</span>
            <span className="text-sm text-yellow-800">
              <strong>Mode Test Stripe</strong> - Aucun paiement réel ne sera effectué
            </span>
          </div>
        </div>
        <CheckoutForm
          total={total}
          onSuccess={onSuccess}
          onError={onError}
        />
      </div>
    </Elements>
  );
};

export default StripeCheckout;