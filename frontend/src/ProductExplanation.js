import React from 'react';

const ProductExplanation = () => {
  return (
    <div className="bg-white py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        
        {/* Section Hero */}
        <div className="text-center mb-16">
          <h2 className="text-4xl font-bold text-gray-900 mb-6">
            🌊 Technologie d'Osmose Inverse et d'Ultrafiltration
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Découvrez comment nos systèmes révolutionnaires transforment l'eau du robinet en eau pure, 
            éliminant 98% des bactéries et 99% des éléments chimiques pour votre santé et celle de votre famille.
          </p>
        </div>

        {/* Problème et Solutions */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-16">
          <div className="bg-red-50 p-8 rounded-2xl">
            <h3 className="text-2xl font-bold text-red-800 mb-6 flex items-center">
              ⚠️ Le Problème : Eau Polluée en Europe
            </h3>
            <div className="space-y-4 text-gray-700">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">🇫🇷</span>
                <span><strong>68 millions</strong> d'habitants en France boivent de l'eau polluée</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-2xl">🇪🇸</span>
                <span><strong>48 millions</strong> d'habitants en Espagne dans la même situation</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-2xl">💰</span>
                <span>Coût élevé des bouteilles : <strong>500-700€ par famille/an</strong></span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-2xl">🌍</span>
                <span>Impact environnemental des plastiques</span>
              </div>
            </div>
          </div>

          <div className="bg-green-50 p-8 rounded-2xl">
            <h3 className="text-2xl font-bold text-green-800 mb-6 flex items-center">
              ✅ Notre Solution : Fontaines Josmose
            </h3>
            <div className="space-y-4 text-gray-700">
              <div className="flex items-center space-x-3">
                <span className="text-2xl">💧</span>
                <span><strong>Eau pure</strong> directement du robinet</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-2xl">💰</span>
                <span><strong>Économie 500-700€</strong> par année</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-2xl">🔧</span>
                <span><strong>Installation simple</strong> sans professionnel</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-2xl">🛡️</span>
                <span><strong>Garantie 1-5 ans</strong> selon option</span>
              </div>
              <div className="flex items-center space-x-3">
                <span className="text-2xl">🌱</span>
                <span><strong>0 déchet plastique</strong></span>
              </div>
            </div>
          </div>
        </div>

        {/* Avantages Compétitifs */}
        <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-8 rounded-2xl mb-16">
          <h3 className="text-3xl font-bold text-center text-gray-900 mb-8">
            🏆 Nos Avantages Compétitifs
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center">
              <div className="text-4xl mb-4">🥇</div>
              <h4 className="text-xl font-bold text-gray-900 mb-2">1er sur le Marché</h4>
              <p className="text-gray-600">Premiers à proposer la fontaine osmosée pour particuliers en France et Espagne</p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-4">🇪🇺</div>
              <h4 className="text-xl font-bold text-gray-900 mb-2">Expansion Européenne</h4>
              <p className="text-gray-600">Objectif : couvrir toute l'Europe avec nos partenaires</p>
            </div>
            <div className="text-center">
              <div className="text-4xl mb-4">👑</div>
              <h4 className="text-xl font-bold text-gray-900 mb-2">Leader Futur</h4>
              <p className="text-gray-600">Devenir le N°1 européen dans les années à venir</p>
            </div>
          </div>
        </div>

        {/* Fonctionnement Osmose Inverse */}
        <div className="mb-16">
          <h3 className="text-3xl font-bold text-center text-gray-900 mb-12">
            🔬 Comment fonctionne l'Osmose Inverse ?
          </h3>
          
          <div className="bg-white border border-gray-200 rounded-2xl p-8 mb-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <div>
                <img 
                  src="https://customer-assets.emergentagent.com/job_water-purifier-hub/artifacts/images/d3d3d1eebf0370a53ed1acfdc3d6364b02f78205a23c1d2428fa69fda91cccf5.jpg"
                  alt="Schéma système osmose inverse"
                  className="w-full h-auto rounded-lg shadow-lg"
                />
              </div>
              <div className="space-y-6">
                <h4 className="text-2xl font-bold text-gray-900">Technologie RO (Osmose Inverse)</h4>
                <div className="space-y-4">
                  <div className="flex items-start space-x-3">
                    <div className="text-2xl">🔬</div>
                    <div>
                      <strong className="text-gray-900">Membrane semi-perméable :</strong>
                      <p className="text-gray-600">Pores microscopiques qui bloquent les contaminants</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="text-2xl">💧</div>
                    <div>
                      <strong className="text-gray-900">Eau purifiée :</strong>
                      <p className="text-gray-600">Seules les molécules d'eau pure passent à travers</p>
                    </div>
                  </div>
                  <div className="flex items-start space-x-3">
                    <div className="text-2xl">🚫</div>
                    <div>
                      <strong className="text-gray-900">Contaminants bloqués :</strong>
                      <p className="text-gray-600">Bactéries, virus, métaux lourds, produits chimiques</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* 4 Étapes de Filtration */}
        <div className="mb-16">
          <h3 className="text-3xl font-bold text-center text-gray-900 mb-12">
            🔄 Les 4 Étapes de Filtration
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
            {/* Étape 1 */}
            <div className="bg-blue-50 p-6 rounded-xl text-center">
              <div className="text-4xl mb-4">1️⃣</div>
              <h4 className="text-lg font-bold text-blue-900 mb-3">Filtre PP</h4>
              <div className="text-sm text-blue-800 space-y-2">
                <p><strong>Polypropylène</strong></p>
                <p>Élimine les grosses particules supérieures à 5 microns</p>
                <p>🔹 Sédiments</p>
                <p>🔹 Rouille</p>
                <p>🔹 Débris visibles</p>
              </div>
            </div>

            {/* Étape 2 */}
            <div className="bg-green-50 p-6 rounded-xl text-center">
              <div className="text-4xl mb-4">2️⃣</div>
              <h4 className="text-lg font-bold text-green-900 mb-3">Filtre GAC</h4>
              <div className="text-sm text-green-800 space-y-2">
                <p><strong>Charbon Actif Granulés</strong></p>
                <p>Retient particules organiques et chlore</p>
                <p>🔹 Chlore</p>
                <p>🔹 Mauvais goût</p>
                <p>🔹 Odeurs</p>
              </div>
            </div>

            {/* Étape 3 */}
            <div className="bg-orange-50 p-6 rounded-xl text-center">
              <div className="text-4xl mb-4">3️⃣</div>
              <h4 className="text-lg font-bold text-orange-900 mb-3">Filtre CTO</h4>
              <div className="text-sm text-orange-800 space-y-2">
                <p><strong>Charbon Actif Bloc</strong></p>
                <p>Élimine le reste du chlore et organiques</p>
                <p>🔹 Chlore résiduel</p>
                <p>🔹 Pesticides</p>
                <p>🔹 Herbicides</p>
              </div>
            </div>

            {/* Étape 4 */}
            <div className="bg-purple-50 p-6 rounded-xl text-center">
              <div className="text-4xl mb-4">4️⃣</div>
              <h4 className="text-lg font-bold text-purple-900 mb-3">Membrane UF</h4>
              <div className="text-sm text-purple-800 space-y-2">
                <p><strong>Ultrafiltration 0.01 micron</strong></p>
                <p>Retient toutes particules > 0.01 micron</p>
                <p>🔹 Virus</p>
                <p>🔹 Bactéries</p>
                <p>🔹 Macromolécules</p>
              </div>
            </div>
          </div>
        </div>

        {/* Efficacité du Traitement */}
        <div className="bg-gradient-to-r from-green-500 to-blue-600 text-white p-8 rounded-2xl mb-16">
          <h3 className="text-3xl font-bold text-center mb-8">
            📊 Efficacité Prouvée de nos Systèmes
          </h3>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="text-center bg-white/10 p-6 rounded-xl">
              <div className="text-3xl font-bold mb-2">98%</div>
              <div className="text-sm">Bactéries éliminées</div>
            </div>
            <div className="text-center bg-white/10 p-6 rounded-xl">
              <div className="text-3xl font-bold mb-2">99%</div>
              <div className="text-sm">Éléments chimiques</div>
            </div>
            <div className="text-center bg-white/10 p-6 rounded-xl">
              <div className="text-3xl font-bold mb-2">98%</div>
              <div className="text-sm">Nitrates supprimés</div>
            </div>
            <div className="text-center bg-white/10 p-6 rounded-xl">
              <div className="text-3xl font-bold mb-2">99%</div>
              <div className="text-sm">Radioactifs bloqués</div>
            </div>
          </div>
        </div>

        {/* Fontaine Ultrafiltration */}
        <div className="mb-16">
          <h3 className="text-3xl font-bold text-center text-gray-900 mb-12">
            🌿 Fontaine d'Ultrafiltration : L'Alternative Écologique
          </h3>
          
          <div className="bg-green-50 border border-green-200 rounded-2xl p-8">
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 items-center">
              <div>
                <img 
                  src="https://customer-assets.emergentagent.com/job_water-purifier-hub/artifacts/images/4c4845180c928079072df07e0fad5c1c2618e3c7926c1539e69c08cc561e02c7.jpg"
                  alt="Fontaine d'ultrafiltration"
                  className="w-full h-auto rounded-lg shadow-lg"
                />
              </div>
              <div className="space-y-6">
                <h4 className="text-2xl font-bold text-green-900">Technologie UF Écologique</h4>
                <div className="space-y-4">
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">🌱</div>
                    <div>
                      <strong className="text-green-900">Zéro rejet d'eau</strong>
                      <p className="text-green-700">Contrairement à l'osmose, aucun gaspillage</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">⚡</div>
                    <div>
                      <strong className="text-green-900">Sans électricité</strong>
                      <p className="text-green-700">Utilise uniquement la pression du réseau</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">🔧</div>
                    <div>
                      <strong className="text-green-900">Installation ultra-simple</strong>
                      <p className="text-green-700">Cartouches à baïonnette pour entretien facile</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3">
                    <div className="text-2xl">💎</div>
                    <div>
                      <strong className="text-green-900">Design élégant</strong>
                      <p className="text-green-700">S'adapte parfaitement à votre cuisine</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Contaminants Éliminés */}
        <div className="mb-16">
          <h3 className="text-3xl font-bold text-center text-gray-900 mb-12">
            🛡️ Contaminants Efficacement Éliminés
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <div className="bg-red-50 p-6 rounded-xl">
              <h4 className="text-lg font-bold text-red-900 mb-4 flex items-center">
                <span className="mr-2">🦠</span>
                Organismes Pathogènes
              </h4>
              <ul className="text-sm text-red-800 space-y-2">
                <li>• Bactéries (E.coli, Salmonella...)</li>
                <li>• Virus (Hépatite, Gastro...)</li>
                <li>• Parasites (Cryptosporidium...)</li>
                <li>• Kystes et spores</li>
              </ul>
            </div>

            <div className="bg-yellow-50 p-6 rounded-xl">
              <h4 className="text-lg font-bold text-yellow-900 mb-4 flex items-center">
                <span className="mr-2">⚗️</span>
                Éléments Chimiques
              </h4>
              <ul className="text-sm text-yellow-800 space-y-2">
                <li>• Chlore et chloramines</li>
                <li>• Métaux lourds (plomb, mercure...)</li>
                <li>• Pesticides et herbicides</li>
                <li>• Nitrates et nitrites</li>
              </ul>
            </div>

            <div className="bg-purple-50 p-6 rounded-xl">
              <h4 className="text-lg font-bold text-purple-900 mb-4 flex items-center">
                <span className="mr-2">☢️</span>
                Substances Toxiques
              </h4>
              <ul className="text-sm text-purple-800 space-y-2">
                <li>• Arsenic et fluorure</li>
                <li>• Éléments radioactifs</li>
                <li>• COV (Composés organiques volatils)</li>
                <li>• Résidus pharmaceutiques</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Installation et Maintenance */}
        <div className="bg-blue-50 p-8 rounded-2xl mb-16">
          <h3 className="text-3xl font-bold text-center text-blue-900 mb-8">
            🔧 Installation et Maintenance Simplifiées
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12">
            <div>
              <h4 className="text-xl font-bold text-blue-900 mb-6">Installation Rapide</h4>
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <span className="text-blue-600 font-bold">1.</span>
                  <div>
                    <strong className="text-blue-900">Raccordement simple</strong>
                    <p className="text-blue-700 text-sm">Se connecte directement à votre arrivée d'eau</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-blue-600 font-bold">2.</span>
                  <div>
                    <strong className="text-blue-900">Aucune électricité</strong>
                    <p className="text-blue-700 text-sm">Fonctionne avec la pression du réseau</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-blue-600 font-bold">3.</span>
                  <div>
                    <strong className="text-blue-900">Test immédiat</strong>
                    <p className="text-blue-700 text-sm">Eau pure disponible instantanément</p>
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h4 className="text-xl font-bold text-blue-900 mb-6">Maintenance Facile</h4>
              <div className="space-y-4">
                <div className="flex items-start space-x-3">
                  <span className="text-blue-600 font-bold">📅</span>
                  <div>
                    <strong className="text-blue-900">Changement tous les 6 mois</strong>
                    <p className="text-blue-700 text-sm">Kit de filtres à 49€ seulement</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-blue-600 font-bold">🔄</span>
                  <div>
                    <strong className="text-blue-900">Cartouches à baïonnette</strong>
                    <p className="text-blue-700 text-sm">Remplacement en quelques minutes</p>
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-blue-600 font-bold">📞</span>
                  <div>
                    <strong className="text-blue-900">Support technique</strong>
                    <p className="text-blue-700 text-sm">Ligne directe pour toute question</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Garanties et Services */}
        <div className="bg-gray-50 p-8 rounded-2xl">
          <h3 className="text-3xl font-bold text-center text-gray-900 mb-8">
            🛡️ Garanties et Services Inclus
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="text-center bg-white p-6 rounded-xl shadow-md">
              <div className="text-4xl mb-4">✅</div>
              <h4 className="text-lg font-bold text-gray-900 mb-3">Garantie Incluse</h4>
              <p className="text-gray-600 text-sm">
                1 an gratuit, extensible à 2 ans (39€) ou 5 ans (59€)
              </p>
            </div>

            <div className="text-center bg-white p-6 rounded-xl shadow-md">
              <div className="text-4xl mb-4">🚚</div>
              <h4 className="text-lg font-bold text-gray-900 mb-3">Livraison Rapide</h4>
              <p className="text-gray-600 text-sm">
                19€ France, 29€ Europe - Équipe logistique dédiée
              </p>
            </div>

            <div className="text-center bg-white p-6 rounded-xl shadow-md">
              <div className="text-4xl mb-4">🎧</div>
              <h4 className="text-lg font-bold text-gray-900 mb-3">Service Client</h4>
              <p className="text-gray-600 text-sm">
                Support technique et ligne directe pour réclamations
              </p>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
};

export default ProductExplanation;