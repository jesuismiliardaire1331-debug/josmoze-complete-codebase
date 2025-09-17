import React, { useState, useEffect, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';
import { useSafeCleanup } from './hooks/useSafeCleanup';

// Configuration
const API_BASE = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

// Base de connaissances enrichie V3 (version frontend) - Intégration contenu validé
const KNOWLEDGE_BASE_V3 = {
  dangers_eau: {
    nitrates: {
      origine: "Agriculture intensive (78% des cas), élevages industriels (15%), eaux usées urbaines (7%)",
      chiffres_choc: "142 cas syndrome bébé bleu recensés depuis 2020, 15% communes dépassent seuils",
      zones_critiques: "Bretagne 68% communes, Champagne-Ardenne 52%, Beauce 45%",
      risques_sante: "Empêchent sang transporter oxygène chez bébés, +18% risque cancer colorectal adultes",
      elimination_josmoze: "98,5% élimination garantie"
    },
    pesticides: {
      chiffres_alarmants: "5,7 pesticides différents par verre en moyenne, 200+ molécules détectées, 68% points contrôle contaminés",
      top_dangers: "Glyphosate 65% (Roundup), Atrazine 78% (interdit mais persistant), Métolachlore 52%",
      effet_cocktail: "Personne ne sait ce qui se passe quand ces molécules se mélangent dans organisme",
      zones_rouges: "Champagne-Ardenne 82%, Centre-Val Loire 79%, Hauts-de-France 76%",
      elimination_josmoze: "99,2% des 200+ molécules éliminées"
    },
    chlore: {
      paradoxe: "Nécessaire pour désinfecter mais crée sous-produits cancérigènes (trihalométhanes)",
      impact_microbiote: "Détruit flore intestinale (-23% diversité en 6 mois), troubles digestifs, affaiblissement immunitaire",
      sous_produits_toxiques: "Trihalométhanes présents 45% réseaux, classés potentiellement cancérigènes",
      elimination_josmoze: "99,8% suppression chlore + sous-produits"
    }
  },
  
  solutions_comparees: {
    carafe_filtrante: {
      avantages: "Simple, améliore goût chlore, prix achat 30-50€",
      inconvenients: "Inefficace nitrates/pesticides, 180€/an filtres, nid bactéries si mal entretenue",
      verdict: "Solution de confort, pas de santé"
    },
    filtre_robinet: {
      avantages: "Filtre chlore + certains pesticides, plus pratique que carafe",
      inconvenients: "N'élimine ni nitrates, ni virus, ni métaux lourds, efficacité diminue vite",
      verdict: "Insuffisant pour protection familiale complète"
    },
    eau_bouteille: {
      problemes: "Microplastiques + 40€/mois famille + désastre écologique",
      comparaison_cout: "40€/mois famille vs 37€/mois osmoseur",
      verdict: "Plus cher et moins écologique qu'osmose"
    },
    osmose_inverse_josmoze: {
      efficacite: "99,9% élimination TOUT, goût parfait, membrane 0,0001 micron",
      economie: "37€/mois 0% vs 40€/mois bouteilles, économies 4800€/5 ans",
      ecologie: "Zéro déchet plastique, -87% empreinte carbone vs eau embouteillée",
      verdict: "Seule solution complète sans compromis"
    }
  },
  
  offres_josmoze: {
    pack_famille: {
      prix_promo: "890€ (au lieu de 1290€) = -31% réduction exclusive",
      financement: "37€/mois sur 24 mois à 0%",
      bonus_animal: "1 produit animal OFFERT au choix (fontaine 49€, sac 29€, distributeur 39€)",
      inclus: "Osmoseur 7 étapes, installation pro, analyse gratuite, formation, filtres 1ère année, app IoT, garantie 5 ans"
    },
    comparaison_economique: {
      vs_bouteilles_5ans: "4800€ économisés",
      roi: "8 mois d'amortissement",
      cout_reel: "0,12€/L vs 0,25€/L bouteille",
      ecologie: "15000 bouteilles évitées/an"
    },
    garanties_exclusives: {
      satisfaction: "30 jours satisfait/remboursé",
      garantie_totale: "5 ans pièces + main d'œuvre",
      installation: "Dégâts couverts pendant installation",
      qualite_vie: "Analyses gratuites à vie"
    }
  },
  
  nouveaux_produits_animaux: {
    fontaine_animaux: {
      prix: "49€",
      description: "Fontaine eau pure pour animaux avec système filtration avancé",
      avantages: "Même technologie osmoseurs, matériaux premium, garantie 2 ans"
    },
    sac_transport: {
      prix: "29€", 
      description: "Sac transport premium pour animaux avec mini-purificateur air intégré",
      avantages: "Ventilation optimisée, filtres anti-odeurs, compatible IATA"
    },
    distributeur_nourriture: {
      prix: "39€",
      description: "Distributeur nourriture intelligent avec intégration mini-fontaine",
      avantages: "Application dédiée, système conservation hermétique, compatible IoT"
    }
  },
  
  temoignages_clients: {
    sophie_lille: "2 ans avec Josmoze. Mes enfants n'ont plus de problèmes digestifs. Je recommande !",
    dr_claire_nice: "En tant que médecin, je salue cette qualité de filtration. Mes patients vont mieux.",
    michel_bordeaux: "Installation parfaite, équipe pro. L'économie sur l'eau en bouteille est impressionnante.",
    note_moyenne: "4,8/5 (847 avis vérifiés)"
  },
  
  arguments_vente_choc: {
    sante_famille: "Élimine 99,9% contaminants (nitrates, pesticides, chlore, métaux, virus, bactéries)",
    economie_prouvee: "ROI 500% sur 10 ans, économies 12710€ vs eau bouteille",
    impact_ecologique: "Zéro déchet plastique, 15000 bouteilles évitées/an/famille",
    technologie_nasa: "Membrane 0,0001 micron, même technologie purification spatiale",
    simplicite_totale: "Robinet dédié, réservoir 12L, maintenance 1 visite/an"
  }
};

  // Système de réponses intelligentes V3 ULTRA-ENRICHI - Intégration contenu validé
  const getIntelligentResponse = (message) => {
    const lowerMessage = message.toLowerCase();
    
    // Détection d'intention V3 ultra-précise
    const intentions = {
      // Intentions santé/dangers - Nouvelles catégories précises
      dangers_bebes: ['bébé', 'nourrisson', 'enfant', 'syndrome', 'bleu', 'oxygène', 'respiration'],
      nitrates_specifique: ['nitrate', 'nitrites', 'agriculture', 'intensive', 'cancer', 'colorectal'],
      pesticides_specifique: ['pesticide', 'glyphosate', 'roundup', 'atrazine', 'cocktail', 'chimique', 'agricole'],
      chlore_specifique: ['chlore', 'javel', 'microbiote', 'intestin', 'trihalométhane', 'cancérigène'],
      zones_geographiques: ['bretagne', 'champagne', 'ardenne', 'beauce', 'région', 'zone', 'commune'],
      
      // Intentions commerciales enrichies
      prix_objection: ['cher', 'coûteux', 'budget', 'moyens', 'financier', 'abordable'],
      prix_demande: ['prix', 'coût', 'tarif', 'combien', '€', 'euro', 'financement'],
      comparaison_precise: ['carafe', 'brita', 'filtre', 'robinet', 'bouteille', 'evian', 'versus', 'vs'],
      economie_roi: ['economie', 'rentable', 'amortissement', 'roi', 'investissement', 'rembourse'],
      
      // Nouvelles intentions produits
      animaux_nouveaute: ['chien', 'chat', 'animal', 'fontaine', 'sac', 'transport', 'distributeur'],
      technologie_nasa: ['technique', 'technologie', 'nasa', 'membrane', 'micron', 'comment', 'fonctionne'],
      installation_service: ['installer', 'installation', 'pose', 'technicien', 'service'],
      garanties_securite: ['garantie', 'sav', 'assurance', 'securite', 'rembourse', 'satisfait'],
      
      // Intentions d'engagement
      urgence_decision: ['urgent', 'rapidement', 'maintenant', 'aujourd'hui', 'vite'],
      hesitation_doute: ['hésite', 'réfléchir', 'pas sûr', 'doute', 'incertain'],
      temoignages_avis: ['avis', 'témoignage', 'retour', 'expérience', 'satisfaction'],
      contact_humain: ['parler', 'contact', 'téléphone', 'rendez-vous', 'expert', 'conseiller'],
      
      // Intentions de base
      salutation: ['bonjour', 'bonsoir', 'salut', 'hello', 'coucou'],
      remerciements: ['merci', 'thanks', 'parfait', 'super', 'génial', 'formidable']
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
    
    // Réponses V3 ultra-enrichies avec données validées
    const responses = {
      // Réponses dangers spécifiques avec données choc
      dangers_bebes: [
        `🚨 ALERTE bébés ! ${KNOWLEDGE_BASE_V3.dangers_eau.nitrates.chiffres_choc}. ${KNOWLEDGE_BASE_V3.dangers_eau.nitrates.risques_sante}. Josmoze élimine ${KNOWLEDGE_BASE_V3.dangers_eau.nitrates.elimination_josmoze}. Bébés à protéger ?`,
        `🍼 DANGER syndrome bébé bleu ! Nitrates empêchent oxygène sang. 142 cas depuis 2020 ! Zones critiques : ${KNOWLEDGE_BASE_V3.dangers_eau.nitrates.zones_critiques}. Sécurité totale avec Josmoze !`
      ],
      
      nitrates_specifique: [
        `⚠️ Nitrates = tueur silencieux ! ${KNOWLEDGE_BASE_V3.dangers_eau.nitrates.origine}. ${KNOWLEDGE_BASE_V3.dangers_eau.nitrates.chiffres_choc}. Votre région touchée ? Protection ${KNOWLEDGE_BASE_V3.dangers_eau.nitrates.elimination_josmoze} !`,
        `🌾 Agriculture intensive = poison quotidien ! 78% nitrates viennent champs. Cancer +18% prouvé. Bretagne 68% communes dépassent seuils. Stoppez maintenant !`
      ],
      
      pesticides_specifique: [
        `☢️ Cocktail chimique terrifiant ! ${KNOWLEDGE_BASE_V3.dangers_eau.pesticides.chiffres_alarmants}. Pires : ${KNOWLEDGE_BASE_V3.dangers_eau.pesticides.top_dangers}. ${KNOWLEDGE_BASE_V3.dangers_eau.pesticides.effet_cocktail} !`,
        `🧪 5,7 pesticides/verre ! Glyphosate 65%, Atrazine 78% ! Zones rouge : ${KNOWLEDGE_BASE_V3.dangers_eau.pesticides.zones_rouges}. Josmoze élimine ${KNOWLEDGE_BASE_V3.dangers_eau.pesticides.elimination_josmoze} !`
      ],
      
      chlore_specifique: [
        `💧 Paradoxe chlore mortel ! ${KNOWLEDGE_BASE_V3.dangers_eau.chlore.paradoxe}. ${KNOWLEDGE_BASE_V3.dangers_eau.chlore.impact_microbiote}. Solution : ${KNOWLEDGE_BASE_V3.dangers_eau.chlore.elimination_josmoze} !`,
        `🦠 Chlore = faux ami ! Tue bactéries mais crée cancérigènes + détruit VOS bonnes bactéries (-23% microbiote). Défenses immunitaires effondrées !`
      ],
      
      zones_geographiques: [
        `🗺️ Votre région à risque ! Bretagne 68%, Champagne 82%, Beauce 45% communes contaminées ! Zones rouges pesticides : ${KNOWLEDGE_BASE_V3.dangers_eau.pesticides.zones_rouges}. Analyse gratuite région ?`,
        `📍 Géographie du danger ! Agriculture intensive = zones à risque maximum. Même zones "vertes" ont chlore + sous-produits cancérigènes. Protection totale nécessaire !`
      ],
      
      // Réponses commerciales optimisées
      prix_objection: [
        `💭 Cher ? Analysons ! ${KNOWLEDGE_BASE_V3.offres_josmoze.pack_famille.financement} vs ${KNOWLEDGE_BASE_V3.solutions_comparees.eau_bouteille.comparaison_cout}. ROI ${KNOWLEDGE_BASE_V3.offres_josmoze.comparaison_economique.roi} ! Santé famille = SANS PRIX !`,
        `💸 Investment intelligent ! 890€ = 2,44€/jour pour eau pure VIE ENTIÈRE ! Économies ${KNOWLEDGE_BASE_V3.offres_josmoze.comparaison_economique.vs_bouteilles_5ans}. Coût réel ${KNOWLEDGE_BASE_V3.offres_josmoze.comparaison_economique.cout_reel} !`
      ],
      
      prix_demande: [
        `💰 Prix CHOC ! ${KNOWLEDGE_BASE_V3.offres_josmoze.pack_famille.prix_promo}. ${KNOWLEDGE_BASE_V3.offres_josmoze.pack_famille.financement}. ${KNOWLEDGE_BASE_V3.offres_josmoze.pack_famille.bonus_animal}. Calcul personnalisé ?`,
        `🎯 Offre exclusive ! 890€ tout inclus : ${KNOWLEDGE_BASE_V3.offres_josmoze.pack_famille.inclus}. Financement 0% ! Moins cher que bouteilles famille !`
      ],
      
      comparaison_precise: [
        `📊 Comparaison IMPITOYABLE ! Carafe Brita : ${KNOWLEDGE_BASE_V3.solutions_comparees.carafe_filtrante.verdict}. Filtre robinet : ${KNOWLEDGE_BASE_V3.solutions_comparees.filtre_robinet.verdict}. OSMOSE JOSMOZE : ${KNOWLEDGE_BASE_V3.solutions_comparees.osmose_inverse_josmoze.verdict} !`,
        `🎯 Guerre des solutions ! Bouteilles : microplastiques + ruine (40€/mois). Carafe : 0% nitrates/pesticides. SEUL JOSMOZE = 99,9% TOUT éliminé !`
      ],
      
      economie_roi: [
        `📈 ROI MONSTRUEUX ! ${KNOWLEDGE_BASE_V3.offres_josmoze.comparaison_economique.roi} + économies ${KNOWLEDGE_BASE_V3.offres_josmoze.comparaison_economique.vs_bouteilles_5ans}. Coût réel ${KNOWLEDGE_BASE_V3.offres_josmoze.comparaison_economique.cout_reel}. Investissement le + rentable !`,
        `💎 Meilleur placement 2025 ! ROI 500% sur 10 ans prouvé. Écologie : ${KNOWLEDGE_BASE_V3.offres_josmoze.comparaison_economique.ecologie}. Famille + planète gagnantes !`
      ],
      
      // Nouveaux produits animaux
      animaux_nouveaute: [
        `🐾 NOUVEAUTÉ révolutionnaire ! ${KNOWLEDGE_BASE_V3.nouveaux_produits_animaux.fontaine_animaux.description} (${KNOWLEDGE_BASE_V3.nouveaux_produits_animaux.fontaine_animaux.prix}), ${KNOWLEDGE_BASE_V3.nouveaux_produits_animaux.sac_transport.description} (${KNOWLEDGE_BASE_V3.nouveaux_produits_animaux.sac_transport.prix}), ${KNOWLEDGE_BASE_V3.nouveaux_produits_animaux.distributeur_nourriture.description} (${KNOWLEDGE_BASE_V3.nouveaux_produits_animaux.distributeur_nourriture.prix}). 1 OFFERT avec osmoseur !`,
        `🐕 Gamme animaux exclusive ! Eau pure pour TOUTE la famille + compagnons. Même technologie spatiale ! 1 produit animal OFFERT. Vos compagnons méritent le meilleur !`
      ],
      
      technologie_nasa: [
        `🚀 Technologie SPATIALE ! ${KNOWLEDGE_BASE_V3.arguments_vente_choc.technologie_nasa}. Force H2O pure, rejette TOUT le reste. 7 étapes brevetées vs 3-5 concurrents. Démonstration ?`,
        `⚛️ Science pure ! Osmose = miracle physique. Pression sépare molécules. Seule eau H2O passe, contaminants rejetés 99,9%. Révolution démocratisée !`
      ],
      
      installation_service: [
        `🔧 Service VIP total ! Installation pro 1h45, technicien certifié, ${KNOWLEDGE_BASE_V3.offres_josmoze.garanties_exclusives.garantie_totale}. ${KNOWLEDGE_BASE_V3.arguments_vente_choc.simplicite_totale}. Disponibilités 7j/7 !`,
        `⚙️ Clé en main ABSOLU ! Analyse → installation → formation → maintenance. 890€ tout compris. Tranquillité totale garantie !`
      ],
      
      garanties_securite: [
        `🛡️ Sécurité MAXIMALE ! ${KNOWLEDGE_BASE_V3.offres_josmoze.garanties_exclusives.satisfaction}, ${KNOWLEDGE_BASE_V3.offres_josmoze.garanties_exclusives.garantie_totale}, ${KNOWLEDGE_BASE_V3.offres_josmoze.garanties_exclusives.qualite_vie}. Risque ZÉRO !`,
        `✅ Promesse blindée ! Installation garantie (dégâts couverts), qualité certifiée vie entière, satisfaction 30j remboursé. Engagement total !`
      ],
      
      // Intentions d'engagement
      urgence_decision: [
        `⚡ URGENT santé famille ! Chaque jour = exposition nitrates/pesticides/chlore. Protection immédiate disponible ! Analyse gratuite 48h. Agissez MAINTENANT !`,
        `🚨 Temps compté ! Offre -31% limitée. Stock osmoseurs réduit. Syndrome bébé bleu +15% cette année. Protection ne peut attendre !`
      ],
      
      hesitation_doute: [
        `🤔 Hésitation normale ! Mais ${KNOWLEDGE_BASE_V3.temoignages_clients.note_moyenne}. Dr Claire Nice : "${KNOWLEDGE_BASE_V3.temoignages_clients.dr_claire_nice}". ${KNOWLEDGE_BASE_V3.offres_josmoze.garanties_exclusives.satisfaction}. Quelle hésitation précise ?`,
        `💭 Analysons doutes ! Coût ? ROI 8 mois. Efficacité ? 99,9% prouvé labo. Installation ? Pro certifié. Garanties ? 5 ans totale. Questions ?`
      ],
      
      temoignages_avis: [
        `⭐ Clients ravis ! ${KNOWLEDGE_BASE_V3.temoignages_clients.note_moyenne}. Sophie Lille : "${KNOWLEDGE_BASE_V3.temoignages_clients.sophie_lille}". Michel Bordeaux : "${KNOWLEDGE_BASE_V3.temoignages_clients.michel_bordeaux}". Rejoignez-les !`,
        `🏆 Satisfaction prouvée ! Dr Claire Nice : "${KNOWLEDGE_BASE_V3.temoignages_clients.dr_claire_nice}". 847 familles témoignent. Résultats 2-6 semaines !`
      ],
      
      contact_humain: [
        `📞 Expert IMMÉDIAT ! Analyse gratuite domicile 15 paramètres. Conseil personnalisé. Réservation josmoze.com ou 0800 123 456. Disponible maintenant !`,
        `🎯 Conseiller dédié ! Diagnostic complet eau + calcul économies + devis sur-mesure. Partout France. Quand vous arrange ?`
      ],
      
      // Messages de base améliorés
      salutation: [
        `👋 Salut ! Thomas expert eau pure Josmoze. ${KNOWLEDGE_BASE_V3.dangers_eau.pesticides.chiffres_alarmants} ! Votre famille boit quoi ? Analyse gratuite révèle dangers cachés !`,
        `😊 Bonjour ! Spécialiste protection familiale. 142 cas bébés, pesticides cocktail, microbiote détruit... Solutions immédiates disponibles. Situation actuelle ?`
      ],
      
      remerciements: [
        `🙏 Mission accomplie ! Protéger familles = ma passion. ${KNOWLEDGE_BASE_V3.temoignages_clients.note_moyenne} familles satisfaites ! Questions ? Analyse gratuite pour aller + loin !`,
        `😊 Avec plaisir ! Santé famille = priorité absolue. Prochaine étape : analyse révèle état réel votre eau. Expert disponible maintenant !`
      ],
      
      default: [
        `🤔 Précisez svp ? Spécialités V3 : dangers spécifiques (nitrates bébés, pesticides cocktail, chlore microbiote), solutions comparées, nouveaux produits animaux, technologie NASA. Focus ?`,
        `💡 Thomas expert V3 ! Nouveautés : base danger enrichie, produits animaux innovants, offres -31%, garanties renforcées. Préoccupation principale ?`
      ]
    };
    
    const intentionResponses = responses[detectedIntention] || responses.default;
    return intentionResponses[Math.floor(Math.random() * intentionResponses.length)];
  };

const ChatBot = () => {
  const { t } = useTranslation();
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [hasShownWelcome, setHasShownWelcome] = useState(false);
  const messagesEndRef = useRef(null);
  const backendUrl = API_BASE;
  const { safeSetTimeout, isMounted } = useSafeCleanup();

  // Messages d'accueil selon la langue
  const welcomeMessages = {
    fr: {
      initial: "👋 Salut ! Thomas, expert eau pure Josmoze. Préoccupé par votre eau du robinet ? Je peux vous éclairer sur les nitrates, pesticides, chlore... Comment puis-je vous aider ?",
      suggestions: [
        "🚨 Dangers eau robinet (nitrates, pesticides, chlore)",
        "💰 Prix et économies (890€ vs bouteilles)",
        "🏆 Pourquoi osmose Josmoze vs carafes/filtres",
        "📞 Analyse gratuite de mon eau",
        "🐾 Nouveaux produits pour animaux"
      ]
    },
    en: {
      initial: "👋 Hello! I'm Thomas, water purification expert at Josmoze. Concerned about tap water contaminants? I can explain the real dangers... How can I help?",
      suggestions: [
        "🚨 Tap water dangers (nitrates, pesticides, chlorine)",
        "💰 Prices and savings (890€ vs bottles)",
        "🏆 Why Josmoze osmosis vs carafes/filters", 
        "📞 Free water analysis",
        "🐾 New animal products range"
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
      // Détecter la langue automatiquement
      const currentLang = window.i18n?.language || 'fr';
      const isFrench = currentLang.startsWith('fr') || 
                      window.location.pathname.includes('/fr') ||
                      localStorage.getItem('i18nextLng')?.startsWith('fr') ||
                      true; // Par défaut français pour JOSMOSE.COM
      
      const currentLangCode = isFrench ? 'fr' : 'en';
      const welcome = welcomeMessages[currentLangCode];
      
      setMessages([
        {
          type: 'bot',
          content: welcome.initial,
          timestamp: new Date().toISOString(),
          suggestions: welcome.suggestions
        }
      ]);
      setHasShownWelcome(true);
    }
  }, [isOpen, hasShownWelcome]);

  // Afficher automatiquement après 10 secondes sur le site
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

  const sendMessage = async (message) => {
    if (!message.trim()) return;

    const userMessage = {
      type: 'user',
      content: message,
      timestamp: new Date().toISOString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Détecter la langue pour Thomas
      const currentLang = window.i18n?.language || 'fr';
      const isFrench = currentLang.startsWith('fr') || 
                      localStorage.getItem('i18nextLng')?.startsWith('fr') ||
                      true; // Par défaut français
      
      console.log('🤖 Thomas sending message:', message, 'Language detected:', isFrench ? 'FR' : 'EN');

      // Appel à l'agent Thomas pour réponse intelligente
      const response = await axios.post(`${backendUrl}/api/ai-agents/chat`, {
        message: message,
        agent: 'thomas',
        context: 'website_chat',
        language: isFrench ? 'french' : 'english'
      }, {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 10000 // 10 secondes timeout
      });

      console.log('🤖 Thomas response:', response.data);

      const botMessage = {
        type: 'bot',
        content: response.data.response || "Je vous écoute ! Comment puis-je vous aider avec nos systèmes de purification d'eau ?",
        timestamp: new Date().toISOString(),
        suggestions: response.data.suggestions || []
      };

      setMessages(prev => [...prev, botMessage]);

    } catch (error) {
      console.error('❌ Erreur chatbot:', error);
      
      // Réponse de fallback intelligente en français
      const fallbackMessage = {
        type: 'bot',
        content: "Je suis temporairement indisponible, mais notre équipe peut vous aider ! 📞 Appelez-nous ou envoyez un email à commercial@josmoze.com",
        timestamp: new Date().toISOString(),
        suggestions: ['💰 Voir les prix', '📞 Contacter l\'équipe', '💧 En savoir plus']
      };

      setMessages(prev => [...prev, fallbackMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    // Logique selon la suggestion
    if (suggestion.includes('prix') || suggestion.includes('prices')) {
      window.scrollTo({
        top: document.querySelector('#products-section')?.offsetTop || 0,
        behavior: 'smooth'
      });
      setIsOpen(false);
    } else if (suggestion.includes('humain') || suggestion.includes('human')) {
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
          title={t('chatbot.open', 'Discuter avec Thomas')}
        >
          <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <div className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center animate-bounce">
            !
          </div>
        </button>
      </div>
    );
  }

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {/* Chat Window */}
      <div className="bg-white rounded-lg shadow-2xl border border-gray-200 w-96 h-96 flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-500 to-blue-600 text-white p-4 rounded-t-lg flex justify-between items-center">
          <div className="flex items-center space-x-2">
            <div className="w-3 h-3 bg-green-400 rounded-full animate-pulse"></div>
            <div>
              <div className="font-semibold">💬 Thomas - Conseiller</div>
              <div className="text-xs opacity-90">Spécialiste purification</div>
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
          {messages.map((message, index) => (
            <div key={index} className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                message.type === 'user' 
                  ? 'bg-blue-500 text-white' 
                  : 'bg-gray-100 text-gray-800'
              }`}>
                <div className="text-sm">{message.content}</div>
                
                {/* Suggestions */}
                {message.suggestions && message.suggestions.length > 0 && (
                  <div className="mt-2 space-y-1">
                    {message.suggestions.map((suggestion, idx) => (
                      <button
                        key={idx}
                        onClick={() => handleSuggestionClick(suggestion)}
                        className="block w-full text-left text-xs bg-white bg-opacity-20 hover:bg-opacity-30 rounded px-2 py-1 transition-colors"
                      >
                        {suggestion}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>
          ))}
          
          {isLoading && (
            <div className="flex justify-start">
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
            🤖 Propulsé par IA • Réponses en temps réel
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatBot;