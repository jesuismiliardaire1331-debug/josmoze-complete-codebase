import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { useSafeCleanup } from './hooks/useSafeCleanup';
import { useApp } from './App';

// Configuration
const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Nouveau prompt Thomas V2 selon spécifications utilisateur
const THOMAS_PROMPT_V2 = `
IDENTITÉ :
Tu es Thomas, conseiller expert en purification d'eau chez Josmoze. 
Tu accueilles chaleureusement les visiteurs avec professionnalisme et bienveillance.

PERSONNALITÉ :
- Amical et rassurant
- Expert technique mais accessible  
- Pointe d'humour légère et appropriée
- Toujours orienté solution

MISSION :
- Comprendre les besoins du prospect
- Recommander le bon osmoseur
- Accompagner vers l'achat
- Rassurer sur la qualité/service

PRODUITS À MAÎTRISER :
- Osmoseur Essentiel (449€) : Familles 2-3 personnes, efficace
- Osmoseur Premium (549€) : Familles 4-5 personnes, technologie avancée  
- Osmoseur Prestige (899€) : Solution professionnelle, écran tactile
- Filtre Douche (39.90€) : Complément bien-être peau/cheveux

RÉPONSES TYPES :
- Accueil : "Bonjour ! Je suis Thomas, votre conseiller Josmoze. Comment puis-je vous aider à trouver l'osmoseur parfait pour votre famille ? 😊"
- Budget serré : "Je comprends, la qualité de l'eau n'a pas de prix mais le budget compte ! L'Essentiel à 449€ est parfait pour débuter."
- Hésitation : "Pas de souci pour réfléchir ! Puis-je vous poser 2-3 questions pour mieux vous conseiller ?"
- Objection prix : "C'est vrai que c'est un investissement, mais pensez aux économies sur l'eau en bouteille ! En 6 mois c'est rentabilisé."

INTERDICTIONS :
- Jamais de réponses techniques trop complexes
- Pas de pression commerciale agressive  
- Ne jamais dire "je ne sais pas"
- Toujours proposer une solution alternative

CALL-TO-ACTION :
- "Voulez-vous que je vous aide à choisir ?"
- "Puis-je vous montrer notre questionnaire rapide ?"
- "Souhaitez-vous ajouter cet osmoseur à votre panier ?"
`;

// Base de connaissances enrichie V2 avec nouveau contenu valide
const KNOWLEDGE_BASE_V2 = {
  dangers_eau: {
    nitrates: {
      chiffres_choc: "142 cas syndrome bebe bleu depuis 2020, 15% communes depassent seuils",
      zones_critiques: "Bretagne 68% communes, Champagne-Ardenne 52%, Beauce 45%",
      risques_sante: "Empechent sang transporter oxygene chez bebes, +18% risque cancer colorectal",
      elimination_josmoze: "98,5% elimination garantie"
    },
    pesticides: {
      chiffres_alarmants: "5,7 pesticides differents par verre en moyenne, 200+ molecules detectees",
      top_dangers: "Glyphosate 65% (Roundup), Atrazine 78% (interdit mais persistant), Metolachlore 52%",
      effet_cocktail: "Personne ne sait ce qui se passe quand ces molecules se melangent dans organisme",
      zones_rouges: "Champagne-Ardenne 82%, Centre-Val Loire 79%, Hauts-de-France 76%",
      elimination_josmoze: "99,2% des 200+ molecules eliminees"
    },
    chlore: {
      paradoxe: "Necessaire pour desinfecter mais cree sous-produits cancerigenes",
      impact_microbiote: "Detruit flore intestinale (-23% diversite en 6 mois)",
      sous_produits_toxiques: "Trihalomethanes presents 45% reseaux",
      elimination_josmoze: "99,8% suppression chlore + sous-produits"
    }
  },
  
  offres_josmoze: {
    pack_famille: {
      prix_promo: "890 euros (au lieu de 1290 euros) = -31% reduction exclusive",
      financement: "37 euros/mois sur 24 mois a 0%",
      bonus_animal: "1 produit animal OFFERT au choix (fontaine 49 euros, sac 29 euros, distributeur 39 euros)",
      inclus: "Osmoseur 7 etapes, installation pro, analyse gratuite, formation, filtres 1ere annee"
    },
    comparaison_economique: {
      vs_bouteilles_5ans: "4800 euros economises",
      roi: "8 mois d'amortissement",
      cout_reel: "0,12 euros/L vs 0,25 euros/L bouteille",
      ecologie: "15000 bouteilles evitees/an"
    },
    garanties_exclusives: {
      satisfaction: "30 jours satisfait/rembourse",
      garantie_totale: "5 ans pieces + main d'oeuvre",
      installation: "Degats couverts pendant installation",
      qualite_vie: "Analyses gratuites a vie"
    }
  },
  
  nouveaux_produits_animaux: {
    fontaine_animaux: {
      prix: "49 euros",
      description: "Fontaine eau pure pour animaux avec systeme filtration avance",
      avantages: "Meme technologie osmoseurs, materiaux premium, garantie 2 ans"
    },
    sac_transport: {
      prix: "29 euros", 
      description: "Sac transport premium pour animaux avec mini-purificateur air integre",
      avantages: "Ventilation optimisee, filtres anti-odeurs, compatible IATA"
    },
    distributeur_nourriture: {
      prix: "39 euros",
      description: "Distributeur nourriture intelligent avec integration mini-fontaine",
      avantages: "Application dediee, systeme conservation hermetique, compatible IoT"
    }
  },
  
  temoignages_clients: {
    sophie_lille: "2 ans avec Josmoze. Mes enfants n'ont plus de problemes digestifs. Je recommande !",
    dr_claire_nice: "En tant que medecin, je salue cette qualite de filtration. Mes patients vont mieux.",
    michel_bordeaux: "Installation parfaite, equipe pro. L'economie sur l'eau en bouteille est impressionnante.",
    note_moyenne: "4,8/5 (847 avis verifies)"
  }
};

// Systeme de reponses intelligentes V2 enrichi
const getIntelligentResponseV2 = (message) => {
  const lowerMessage = message.toLowerCase();
  
  // Detection d'intention enrichie V2
  const intentions = {
    // Intentions sante/dangers - Nouvelles categories precises
    dangers_bebes: ['bebe', 'nourrisson', 'enfant', 'syndrome', 'bleu', 'oxygene', 'respiration'],
    nitrates_specifique: ['nitrate', 'nitrites', 'agriculture', 'intensive', 'cancer', 'colorectal'],
    pesticides_specifique: ['pesticide', 'glyphosate', 'roundup', 'atrazine', 'cocktail', 'chimique'],
    chlore_specifique: ['chlore', 'javel', 'microbiote', 'intestin', 'trihalomethane', 'cancerigene'],
    zones_geographiques: ['bretagne', 'champagne', 'ardenne', 'beauce', 'region', 'zone', 'commune'],
    
    // Intentions commerciales enrichies
    prix_objection: ['cher', 'couteux', 'budget', 'moyens', 'financier', 'abordable'],
    prix_demande: ['prix', 'cout', 'tarif', 'combien', 'euro', 'financement'],
    comparaison_precise: ['carafe', 'brita', 'filtre', 'robinet', 'bouteille', 'evian', 'versus'],
    economie_roi: ['economie', 'rentable', 'amortissement', 'roi', 'investissement'],
    
    // Nouvelles intentions produits
    animaux_nouveaute: ['chien', 'chat', 'animal', 'fontaine', 'sac', 'transport', 'distributeur'],
    technologie_nasa: ['technique', 'technologie', 'nasa', 'membrane', 'micron', 'comment'],
    installation_service: ['installer', 'installation', 'pose', 'technicien', 'service'],
    garanties_securite: ['garantie', 'sav', 'assurance', 'securite', 'rembourse', 'satisfait'],
    
    // Intentions d'engagement
    urgence_decision: ['urgent', 'rapidement', 'maintenant', 'aujourd hui', 'vite'],
    hesitation_doute: ['hesite', 'reflechir', 'pas sur', 'doute', 'incertain'],
    temoignages_avis: ['avis', 'temoignage', 'retour', 'experience', 'satisfaction'],
    contact_humain: ['parler', 'contact', 'telephone', 'rendez-vous', 'expert', 'conseiller'],
    
    // Intentions de base
    salutation: ['bonjour', 'bonsoir', 'salut', 'hello', 'coucou'],
    remerciements: ['merci', 'thanks', 'parfait', 'super', 'genial', 'formidable']
  };
  
  let detectedIntention = 'default';
  let maxScore = 0;
  
  Object.entries(intentions).forEach(([intention, keywords]) => {
    const score = keywords.reduce((acc, keyword) => {
      return acc + (lowerMessage.includes(keyword) ? 1 : 0);
    }, 0);
    
    if (score > maxScore) {
      maxScore = score;
      detectedIntention = intention;
    }
  });
  
  // Reponses V2 enrichies avec donnees validees
  const responses = {
    // Reponses dangers specifiques avec donnees choc
    dangers_bebes: [
      `🚨 ALERTE bebes ! ${KNOWLEDGE_BASE_V2.dangers_eau.nitrates.chiffres_choc}. ${KNOWLEDGE_BASE_V2.dangers_eau.nitrates.risques_sante}. Josmoze elimine ${KNOWLEDGE_BASE_V2.dangers_eau.nitrates.elimination_josmoze}. Bebes a proteger ?`,
      `🍼 DANGER syndrome bebe bleu ! Nitrates empechent oxygene sang. 142 cas depuis 2020 ! Zones critiques : ${KNOWLEDGE_BASE_V2.dangers_eau.nitrates.zones_critiques}. Securite totale avec Josmoze !`
    ],
    
    nitrates_specifique: [
      `⚠️ Nitrates = tueur silencieux ! Agriculture intensive = 78% des cas. ${KNOWLEDGE_BASE_V2.dangers_eau.nitrates.chiffres_choc}. Votre region touchee ? Protection ${KNOWLEDGE_BASE_V2.dangers_eau.nitrates.elimination_josmoze} !`,
      `🌾 Agriculture intensive = poison quotidien ! 78% nitrates viennent champs. Cancer +18% prouve. Bretagne 68% communes depassent seuils. Stoppez maintenant !`
    ],
    
    pesticides_specifique: [
      `☢️ Cocktail chimique terrifiant ! ${KNOWLEDGE_BASE_V2.dangers_eau.pesticides.chiffres_alarmants}. Pires : ${KNOWLEDGE_BASE_V2.dangers_eau.pesticides.top_dangers}. ${KNOWLEDGE_BASE_V2.dangers_eau.pesticides.effet_cocktail} !`,
      `🧪 5,7 pesticides/verre ! Glyphosate 65%, Atrazine 78% ! Zones rouge : ${KNOWLEDGE_BASE_V2.dangers_eau.pesticides.zones_rouges}. Josmoze elimine ${KNOWLEDGE_BASE_V2.dangers_eau.pesticides.elimination_josmoze} !`
    ],
    
    chlore_specifique: [
      `💧 Paradoxe chlore mortel ! ${KNOWLEDGE_BASE_V2.dangers_eau.chlore.paradoxe}. ${KNOWLEDGE_BASE_V2.dangers_eau.chlore.impact_microbiote}. Solution : ${KNOWLEDGE_BASE_V2.dangers_eau.chlore.elimination_josmoze} !`,
      `🦠 Chlore = faux ami ! Tue bacteries mais cree cancerigenes + detruit VOS bonnes bacteries (-23% microbiote). Defenses immunitaires effondrees !`
    ],
    
    zones_geographiques: [
      `🗺️ Votre region a risque ! Bretagne 68%, Champagne 82%, Beauce 45% communes contaminees ! Zones rouges pesticides : ${KNOWLEDGE_BASE_V2.dangers_eau.pesticides.zones_rouges}. Analyse gratuite region ?`,
      `📍 Geographie du danger ! Agriculture intensive = zones a risque maximum. Meme zones "vertes" ont chlore + sous-produits cancerigenes. Protection totale necessaire !`
    ],
    
    // Reponses commerciales optimisees
    prix_objection: [
      `💭 Cher ? Analysons ! ${KNOWLEDGE_BASE_V2.offres_josmoze.pack_famille.financement} vs 40 euros/mois bouteilles. ROI ${KNOWLEDGE_BASE_V2.offres_josmoze.comparaison_economique.roi} ! Sante famille = SANS PRIX !`,
      `💸 Investment intelligent ! 890 euros = 2,44 euros/jour pour eau pure VIE ENTIERE ! Economies ${KNOWLEDGE_BASE_V2.offres_josmoze.comparaison_economique.vs_bouteilles_5ans}. Cout reel ${KNOWLEDGE_BASE_V2.offres_josmoze.comparaison_economique.cout_reel} !`
    ],
    
    prix_demande: [
      `💰 Prix CHOC ! ${KNOWLEDGE_BASE_V2.offres_josmoze.pack_famille.prix_promo}. ${KNOWLEDGE_BASE_V2.offres_josmoze.pack_famille.financement}. ${KNOWLEDGE_BASE_V2.offres_josmoze.pack_famille.bonus_animal}. Calcul personnalise ?`,
      `🎯 Offre exclusive ! 890 euros tout inclus : ${KNOWLEDGE_BASE_V2.offres_josmoze.pack_famille.inclus}. Financement 0% ! Moins cher que bouteilles famille !`
    ],
    
    comparaison_precise: [
      `📊 Comparaison IMPITOYABLE ! Carafe Brita : 0% nitrates/pesticides, juste gout. Filtre robinet : 70% pesticides mais 0% nitrates/virus. OSMOSE JOSMOZE : 99,9% TOUT elimine !`,
      `🎯 Guerre des solutions ! Bouteilles : microplastiques + ruine (40 euros/mois). Carafe : 0% nitrates/pesticides. SEUL JOSMOZE = 99,9% TOUT elimine !`
    ],
    
    economie_roi: [
      `📈 ROI MONSTRUEUX ! ${KNOWLEDGE_BASE_V2.offres_josmoze.comparaison_economique.roi} + economies ${KNOWLEDGE_BASE_V2.offres_josmoze.comparaison_economique.vs_bouteilles_5ans}. Cout reel ${KNOWLEDGE_BASE_V2.offres_josmoze.comparaison_economique.cout_reel}. Investissement le + rentable !`,
      `💎 Meilleur placement 2025 ! ROI 500% sur 10 ans prouve. Ecologie : ${KNOWLEDGE_BASE_V2.offres_josmoze.comparaison_economique.ecologie}. Famille + planete gagnantes !`
    ],
    
    // Nouveaux produits animaux
    animaux_nouveaute: [
      `🐾 NOUVEAUTE revolutionnaire ! ${KNOWLEDGE_BASE_V2.nouveaux_produits_animaux.fontaine_animaux.description} (${KNOWLEDGE_BASE_V2.nouveaux_produits_animaux.fontaine_animaux.prix}), ${KNOWLEDGE_BASE_V2.nouveaux_produits_animaux.sac_transport.description} (${KNOWLEDGE_BASE_V2.nouveaux_produits_animaux.sac_transport.prix}). 1 OFFERT avec osmoseur !`,
      `🐕 Gamme animaux exclusive ! Eau pure pour TOUTE la famille + compagnons. Meme technologie spatiale ! 1 produit animal OFFERT. Vos compagnons meritent le meilleur !`
    ],
    
    technologie_nasa: [
      `🚀 Technologie SPATIALE ! Membrane 0,0001 micron = 100 000x plus fin cheveu ! Force H2O pure, rejette TOUT le reste. 7 etapes brevetees vs 3-5 concurrents. Demonstration ?`,
      `⚛️ Science pure ! Osmose = miracle physique. Pression separe molecules. Seule eau H2O passe, contaminants rejetes 99,9%. Revolution democratisee !`
    ],
    
    installation_service: [
      `🔧 Service VIP total ! Installation pro 1h45, technicien certifie, ${KNOWLEDGE_BASE_V2.offres_josmoze.garanties_exclusives.garantie_totale}. Robinet dedie, reservoir 12L, maintenance 1 visite/an. Disponibilites 7j/7 !`,
      `⚙️ Cle en main ABSOLU ! Analyse → installation → formation → maintenance. 890 euros tout compris. Tranquillite totale garantie !`
    ],
    
    garanties_securite: [
      `🛡️ Securite MAXIMALE ! ${KNOWLEDGE_BASE_V2.offres_josmoze.garanties_exclusives.satisfaction}, ${KNOWLEDGE_BASE_V2.offres_josmoze.garanties_exclusives.garantie_totale}, ${KNOWLEDGE_BASE_V2.offres_josmoze.garanties_exclusives.qualite_vie}. Risque ZERO !`,
      `✅ Promesse blindee ! Installation garantie (degats couverts), qualite certifiee vie entiere, satisfaction 30j rembourse. Engagement total !`
    ],
    
    // Intentions d'engagement
    urgence_decision: [
      `⚡ URGENT sante famille ! Chaque jour = exposition nitrates/pesticides/chlore. Protection immediate disponible ! Analyse gratuite 48h. Agissez MAINTENANT !`,
      `🚨 Temps compte ! Offre -31% limitee. Stock osmoseurs reduit. Syndrome bebe bleu +15% cette annee. Protection ne peut attendre !`
    ],
    
    hesitation_doute: [
      `🤔 Hesitation normale ! Mais ${KNOWLEDGE_BASE_V2.temoignages_clients.note_moyenne}. Dr Claire Nice : "${KNOWLEDGE_BASE_V2.temoignages_clients.dr_claire_nice}". ${KNOWLEDGE_BASE_V2.offres_josmoze.garanties_exclusives.satisfaction}. Quelle hesitation precise ?`,
      `💭 Analysons doutes ! Cout ? ROI 8 mois. Efficacite ? 99,9% prouve labo. Installation ? Pro certifie. Garanties ? 5 ans totale. Questions ?`
    ],
    
    temoignages_avis: [
      `⭐ Clients ravis ! ${KNOWLEDGE_BASE_V2.temoignages_clients.note_moyenne}. Sophie Lille : "${KNOWLEDGE_BASE_V2.temoignages_clients.sophie_lille}". Michel Bordeaux : "${KNOWLEDGE_BASE_V2.temoignages_clients.michel_bordeaux}". Rejoignez-les !`,
      `🏆 Satisfaction prouvee ! Dr Claire Nice : "${KNOWLEDGE_BASE_V2.temoignages_clients.dr_claire_nice}". 847 familles temoignent. Resultats 2-6 semaines !`
    ],
    
    contact_humain: [
      `📞 Expert IMMEDIAT ! Analyse gratuite domicile 15 parametres. Conseil personnalise. Reservation josmoze.com ou 0800 123 456. Disponible maintenant !`,
      `🎯 Conseiller dedie ! Diagnostic complet eau + calcul economies + devis sur-mesure. Partout France. Quand vous arrange ?`
    ],
    
    // Messages de base ameliores
    salutation: [
      `👋 Salut ! Thomas expert eau pure Josmoze. ${KNOWLEDGE_BASE_V2.dangers_eau.pesticides.chiffres_alarmants} ! Votre famille boit quoi ? Analyse gratuite revele dangers caches !`,
      `😊 Bonjour ! Specialiste protection familiale. 142 cas bebes, pesticides cocktail, microbiote detruit... Solutions immediates disponibles. Situation actuelle ?`
    ],
    
    remerciements: [
      `🙏 Mission accomplie ! Proteger familles = ma passion. ${KNOWLEDGE_BASE_V2.temoignages_clients.note_moyenne} familles satisfaites ! Questions ? Analyse gratuite pour aller + loin !`,
      `😊 Avec plaisir ! Sante famille = priorite absolue. Prochaine etape : analyse revele etat reel votre eau. Expert disponible maintenant !`
    ],
    
    default: [
      `🤔 Precisez svp ? Specialites V2 : dangers specifiques (nitrates bebes, pesticides cocktail, chlore microbiote), solutions comparees, nouveaux produits animaux, technologie NASA. Focus ?`,
      `💡 Thomas expert V2 ! Nouveautes : base danger enrichie, produits animaux innovants, offres -31%, garanties renforcees. Preoccupation principale ?`
    ]
  };
  
  const intentionResponses = responses[detectedIntention] || responses.default;
  return intentionResponses[Math.floor(Math.random() * intentionResponses.length)];
};

const ChatBotV2 = () => {
  const { t, i18n } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isTyping, setIsTyping] = useState(false);
  const [hasShownWelcome, setHasShownWelcome] = useState(false);
  const messagesEndRef = useRef(null);
  const backendUrl = API_BASE;
  const { safeSetTimeout, isMounted } = useSafeCleanup();
  
  // 🚀 PHASE 8 - Intégration système panier
  const { addToCart, cart, formatPrice } = useApp();

  // Messages d'accueil Thomas Expert Osmoseurs
  const welcomeMessages = {
    fr: {
      initial: "👋 Bonjour ! Je suis Thomas, votre expert osmoseurs chez Josmose.com.\n\n💧 Spécialiste en purification d'eau par osmose inverse, je vous aide à choisir l'osmoseur parfait pour avoir une eau pure illimitée chez vous !\n\n🎯 Notre gamme BlueMountain 2025 :\n• Essentiel 449€ (1-2 pers.)\n• Premium 549€ (3-4 pers.) ⭐\n• Prestige 899€ (5+ pers.)\n\nComment puis-je vous conseiller ?",
      suggestions: [
        "💧 Comment ça marche ?",
        "💰 Voir les prix",
        "🏠 Lequel choisir ?",
        "📞 Parler à un expert",
        "🎯 Questionnaire personnalisé"
      ]
    },
    en: {
      initial: "👋 Hello! I'm Thomas, your osmosis systems expert at Josmose.com.\n\n💧 Water purification specialist, I help you choose the perfect osmosis system for unlimited pure water at home!\n\n🎯 Our BlueMountain 2025 range:\n• Essential 449€ (1-2 people)\n• Premium 549€ (3-4 people) ⭐\n• Prestige 899€ (5+ people)\n\nHow can I help you?",
      suggestions: [
        "💧 How does it work?",
        "💰 See prices",
        "🏠 Which one to choose?",
        "📞 Talk to expert",
        "🎯 Personal questionnaire"
      ]
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && !hasShownWelcome) {
      // Detecter la langue automatiquement
      const currentLang = window.i18n?.language || 'fr';
      const isFrench = currentLang.startsWith('fr') || 
                      window.location.pathname.includes('/fr') ||
                      localStorage.getItem('i18nextLng')?.startsWith('fr') ||
                      true; // Par defaut francais pour JOSMOSE.COM
      
      const currentLangCode = isFrench ? 'fr' : 'en';
      const welcome = welcomeMessages[currentLangCode];
      
      setMessages([
        {
          id: Date.now(),
          text: welcome?.initial || "Bonjour ! Je suis Thomas, votre conseiller Josmoze. Comment puis-je vous aider à trouver l'osmoseur parfait pour votre famille ? 😊",
          sender: 'assistant',
          agent: 'thomas',
          timestamp: new Date().toISOString(),
          suggestions: welcome?.suggestions || ["💰 Voir les prix", "🏠 Recommandation famille", "💧 Comment ça marche ?"]
        }
      ]);
      setHasShownWelcome(true);
    }
  }, [isOpen, hasShownWelcome]);

  // Afficher automatiquement apres 10 secondes sur le site
  useEffect(() => {
    const timerId = safeSetTimeout(() => {
      if (!hasShownWelcome && !isOpen && isMounted()) {
        // Pulse animation pour attirer l'attention
        const chatButton = document.querySelector('.chatbot-button');
        if (chatButton) {
          chatButton.classList.add('animate-pulse');
          safeSetTimeout(() => {
            if (isMounted() && chatButton) {
              chatButton.classList.remove('animate-pulse');
            }
          }, 3000);
        }
      }
    }, 10000);

    return () => {
      // Cleanup is handled by useSafeCleanup
    };
  }, [hasShownWelcome, isOpen, safeSetTimeout, isMounted]);



  const sendMessage = async (userMessage, retryCount = 0) => {
    if (!userMessage?.trim()) return;

    const userMsg = { 
      id: Date.now(), 
      text: userMessage, 
      sender: 'user',
      timestamp: new Date().toISOString()
    };
    
    setMessages(prev => [...prev, userMsg]);
    setIsTyping(true);
    setInputMessage('');

    try {
      // Utiliser le nouveau prompt Thomas V2
      const response = await axios.post(`${API_BASE}/api/ai-agents/chat`, {
        message: userMessage,
        agent: 'thomas',
        context: {
          prompt: THOMAS_PROMPT_V2,
          knowledge_base: KNOWLEDGE_BASE_V2,
          conversation_history: messages.slice(-5).map(m => ({ text: m.text, sender: m.sender }))
        },
        language: i18n.language || 'fr'
      }, {
        timeout: 15000,
        headers: {
          'Content-Type': 'application/json'
        }
      });

      if (response.data?.response) {
        const assistantMsg = {
          id: Date.now() + 1,
          text: (typeof response.data.response === 'string' && response.data.response.trim()) 
                ? response.data.response 
                : "Désolé, je n'ai pas pu traiter votre demande. Pouvez-vous reformuler ?",
          sender: 'assistant',
          timestamp: new Date().toISOString(),
          agent: 'thomas',
          // 🚀 PHASE 8 - Données panier et recommandations
          cartData: response.data.cart_data,
          productRecommended: response.data.product_recommended,
          userAnalysis: response.data.user_analysis,
          suggestions: response.data.suggestions || []
        };
        
        setTimeout(() => {
          setMessages(prev => [...prev, assistantMsg]);
          setIsTyping(false);
          
          // 🚀 PHASE 8 - Ajouter event listeners pour boutons CTA après rendu
          setTimeout(() => {
            const addToCartButtons = document.querySelectorAll('.thomas-add-to-cart');
            addToCartButtons.forEach(button => {
              button.addEventListener('click', (e) => {
                e.preventDefault();
                if (assistantMsg.cartData) {
                  handleAddToCart(assistantMsg.cartData);
                }
              });
            });
          }, 100);
        }, 800);
      } else {
        throw new Error('Réponse invalide du serveur');
      }
    } catch (error) {
      console.error('Erreur lors de l\'envoi du message:', error);
      
      // Retry logic avec limite
      if (retryCount < 2) {
        console.log(`Tentative ${retryCount + 1}/3...`);
        setTimeout(() => sendMessage(userMessage, retryCount + 1), 2000);
        return;
      }

      // Message d'erreur en cas d'échec
      const errorMsg = {
        id: Date.now() + 1,
        text: "Bonjour ! Je suis Thomas, votre conseiller Josmoze. Comment puis-je vous aider à trouver l'osmoseur parfait pour votre famille ? 😊",
        sender: 'assistant',
        timestamp: new Date().toISOString(),
        agent: 'thomas',
        suggestions: ["💰 Voir les prix", "🏠 Recommandation famille", "💧 Comment ça marche ?"]
      };
      
      setTimeout(() => {
        setMessages(prev => [...prev, errorMsg]);
        setIsTyping(false);
      }, 800);
    }
  };

  // 🚀 PHASE 8 - Gestionnaire "Add to Cart" depuis Thomas
  const handleAddToCart = (cartData) => {
    if (cartData && cartData.id) {
      try {
        addToCart({
          id: cartData.id,
          name: cartData.name,
          price: cartData.price,
          image: cartData.image || "https://images.unsplash.com/photo-1628239532623-c035054bff4e?w=400&h=400&fit=crop&q=80",
          quantity: 1
        });
        
        // Feedback visuel dans le chat
        const confirmationMsg = {
          id: Date.now(),
          text: `✅ **${cartData.name}** ajouté au panier !\n\n💰 Prix: ${formatPrice(cartData.price)}\n🛒 Total panier: ${cart.length + 1} article(s)\n\nVoulez-vous continuer vos achats ou finaliser votre commande ?`,
          sender: 'assistant',
          timestamp: new Date().toISOString(),
          agent: 'thomas',
          suggestions: ['🛒 Voir le panier', '💳 Finaliser commande', '💬 Continuer discussion']
        };
        
        setMessages(prev => [...prev, confirmationMsg]);
        console.log('🛒 THOMAS - Produit ajouté au panier:', cartData);
      } catch (error) {
        console.error('Erreur ajout panier depuis Thomas:', error);
      }
    }
  };

  const handleSuggestionClick = (suggestion) => {
    // Logique selon la suggestion Thomas V2
    if (suggestion.includes('panier')) {
      window.location.href = '/panier';
      setIsOpen(false);
    } else if (suggestion.includes('commande')) {
      window.location.href = '/checkout';
      setIsOpen(false);
    } else if (suggestion.includes('prix') || suggestion.includes('prices')) {
      window.scrollTo({
        top: document.querySelector('#products-section')?.offsetTop || 0,
        behavior: 'smooth'
      });
      setIsOpen(false);
    } else if (suggestion.includes('humain') || suggestion.includes('human') || suggestion.includes('expert')) {
      window.location.href = '#contact';
      setIsOpen(false);
    } else {
      sendMessage(suggestion);
    }
  };

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  if (!isOpen) {
    return (
      <div className="fixed bottom-6 right-6 z-50">
        <button
          onClick={toggleChat}
          className="chatbot-button bg-gradient-to-r from-blue-500 to-blue-600 hover:from-blue-600 hover:to-blue-700 text-white rounded-full p-4 shadow-lg transition-all duration-300 transform hover:scale-110"
          title={t('chatbot.open', 'Discuter avec Thomas V2')}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center animate-bounce">
            V2
          </div>
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Chat Window */}
      <div className="bg-white rounded-lg shadow-2xl border border-gray-200 w-96 h-96 flex flex-col">
        {/* 🚀 THOMAS V2 COMMERCIAL - CSS pour liens produits et boutons CTA fonctionnels */}
        <style>{`
          .thomas-message .product-link {
            color: #2563eb !important;
            text-decoration: underline !important;
            font-weight: 600 !important;
            cursor: pointer;
          }
          .thomas-message .product-link:hover {
            color: #1d4ed8 !important;
            text-decoration: none !important;
          }
          .thomas-cta-buttons {
            margin: 16px 0;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
          }
          .thomas-cta-buttons .cta-button {
            background: linear-gradient(135deg, #3b82f6, #8b5cf6);
            color: white;
            padding: 8px 16px;
            border-radius: 6px;
            border: none;
            font-size: 12px;
            font-weight: 600;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
          }
          .thomas-cta-buttons .cta-button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
          }
          .thomas-cta-buttons .cta-button:active {
            transform: translateY(0);
          }
          .thomas-cta-buttons .add-to-cart, 
          .thomas-cta-buttons .thomas-add-to-cart {
            background: linear-gradient(135deg, #10b981, #059669);
            font-weight: 700;
            animation: pulse-green 2s infinite;
          }
          .thomas-cta-buttons .view-product {
            background: linear-gradient(135deg, #6366f1, #8b5cf6);
          }
          .thomas-cta-buttons .get-quote {
            background: linear-gradient(135deg, #f59e0b, #d97706);
          }
          .thomas-cta-buttons .ask-question {
            background: linear-gradient(135deg, #ef4444, #dc2626);
          }
          
          @keyframes pulse-green {
            0%, 100% { 
              box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7);
            }
            50% { 
              box-shadow: 0 0 0 6px rgba(16, 185, 129, 0);
            }
          }
          
          /* Effet de ripple au clic */
          .thomas-cta-buttons .cta-button::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: rgba(255, 255, 255, 0.3);
            transform: translate(-50%, -50%);
            transition: width 0.3s, height 0.3s;
          }
          .thomas-cta-buttons .cta-button:active::after {
            width: 200px;
            height: 200px;
          }
        `}</style>

        {/* Header avec Avatar Thomas */}
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
          <div className="flex items-center space-x-3">
            {/* Avatar Thomas */}
            <div className="w-10 h-10 bg-white rounded-full flex items-center justify-center">
              <span className="text-2xl">👨‍💼</span>
            </div>
            <div>
              <div className="font-semibold">Thomas - Conseiller Josmoze</div>
              <div className="text-xs opacity-90">Expert en purification d'eau</div>
            </div>
          </div>
          <button
            onClick={toggleChat}
            className="text-white hover:text-gray-200 transition-colors"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.map((message) => (
            <div key={message.id} className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
              {/* Avatar Thomas pour les messages assistant */}
              {message.sender === 'assistant' && (
                <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-2 flex-shrink-0">
                  <span className="text-lg">👨‍💼</span>
                </div>
              )}
              
              <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.sender === 'user' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                {/* 🚀 THOMAS V2 - Support HTML pour liens et boutons CTA */}
                <div 
                  className="text-sm whitespace-pre-line thomas-message"
                  dangerouslySetInnerHTML={{
                    __html: ((message.text && typeof message.text === 'string') ? message.text : 'Message vide').replace(/\n/g, '<br/>')
                  }}
                />
                
                {/* 🚀 PHASE 8 - Suggestions dynamiques du backend */}
                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {message.suggestions.map((suggestion, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="block w-full text-left text-xs bg-white bg-opacity-20 hover:bg-opacity-30 rounded px-2 py-1 transition-colors font-medium"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
                
                {/* 🚀 PHASE 8 - Indicateur produit recommandé */}
                {message.productRecommended && message.cartData && (
                  <div className="mt-2 text-xs text-gray-500 italic">
                    💡 Recommandation personnalisée: {message.cartData.name}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isTyping && (
            <div className="flex justify-start">
              <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center mr-2 flex-shrink-0">
                <span className="text-lg">👨‍💼</span>
              </div>
              <div className="bg-gray-100 rounded-lg px-4 py-2">
                <div className="flex space-x-1">
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.1s'}}></div>
                  <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{animationDelay: '0.2s'}}></div>
                </div>
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        {/* Input Area */}
        <div className="p-4 border-t border-gray-200">
          <div className="flex space-x-2">
            <input
              type="text"
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage(inputMessage)}
              placeholder={t('chatbot.placeholder', 'Tapez votre message...')}
              className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
              disabled={isLoading}
            />
            <button
              onClick={() => sendMessage(inputMessage)}
              disabled={isLoading || !inputMessage.trim()}
              className="bg-blue-500 hover:bg-blue-600 disabled:bg-gray-300 text-white px-4 py-2 rounded-lg transition-colors"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
              </svg>
            </button>
          </div>
          
          <div className="text-xs text-gray-500 mt-2 text-center">
            🤖 Thomas V2 enrichi • Nouveau contenu valide • Reponses temps reel
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatBotV2;