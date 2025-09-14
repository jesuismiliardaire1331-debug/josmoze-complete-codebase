import React, { useEffect, useState, useRef } from 'react';
import { useTranslation } from 'react-i18next';
import axios from 'axios';

class TranslationGuardian {
  constructor() {
    this.isActive = true;
    this.lastLanguage = null;
    this.translationCache = {};
    this.pendingElements = new Set();
    this.retryAttempts = 0;
    this.maxRetries = 3;
    this.checkInterval = 2000; // Check every 2 seconds
    this.backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';
    
    console.log('🛡️ Translation Guardian initialized - Protecting language consistency');
    this.startMonitoring();
  }

  startMonitoring() {
    setInterval(() => {
      if (this.isActive) {
        this.performLanguageCheck();
      }
    }, this.checkInterval);
  }

  async performLanguageCheck() {
    try {
      const currentLanguage = window.i18n?.language || 'fr';
      
      // If language changed, force complete retranslation
      if (this.lastLanguage && this.lastLanguage !== currentLanguage) {
        console.log(`🔄 Language change detected: ${this.lastLanguage} → ${currentLanguage}`);
        await this.forceCompleteRetranslation(currentLanguage);
      }
      
      // Always check for untranslated content
      await this.scanForUntranslatedContent(currentLanguage);
      
      this.lastLanguage = currentLanguage;
      
    } catch (error) {
      console.error('❌ Translation Guardian error:', error);
    }
  }

  async forceCompleteRetranslation(targetLanguage) {
    console.log('🚀 FORCE AGGRESSIVE: Complete page retranslation to:', targetLanguage);
    
    try {
      // Force immediate page updates
      await this.forceAllTextElements(targetLanguage);
      
      // Force React re-render with language change event
      this.triggerLanguageChange(targetLanguage);
      
      // Force retranslation of all hardcoded texts
      await this.translateHardcodedTexts(targetLanguage);
      
      console.log(`✅ AGGRESSIVE retranslation completed`);
      
    } catch (error) {
      console.error('❌ Complete retranslation failed:', error);
      if (this.retryAttempts < this.maxRetries) {
        this.retryAttempts++;
        setTimeout(() => this.forceCompleteRetranslation(targetLanguage), 1000);
      }
    }
  }

  async forceAllTextElements(targetLanguage) {
    if (targetLanguage === 'fr') return; // French is default
    
    // Get ALL text elements including hardcoded ones
    const allTextSelectors = [
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'p', 'span', 'div', 'button', 'a', 'label',
      '[class*="text"]', '[class*="title"]', '[class*="description"]',
      '[class*="content"]', '[class*="label"]', '[class*="feature"]',
      '[class*="price"]', '[class*="product"]', '[class*="cart"]'
    ];
    
    for (const selector of allTextSelectors) {
      const elements = document.querySelectorAll(selector);
      for (const element of elements) {
        if (this.hasTranslatableText(element)) {
          await this.translateElement(element, targetLanguage);
        }
      }
    }
  }

  async translateHardcodedTexts(targetLanguage) {
    const hardcodedTranslations = {
      'en': {
        'Élimination Totale': 'Total Elimination',
        'Installation Simple': 'Simple Installation', 
        'Économies Garanties': 'Guaranteed Savings',
        'Capacité Industrielle': 'Industrial Capacity',
        'Monitoring Avancé': 'Advanced Monitoring',
        'Support Dédié': 'Dedicated Support',
        'Pourquoi Choisir Nos Systèmes?': 'Why Choose Our Systems?',
        'Pourquoi Choisir Nos Solutions Pro?': 'Why Choose Our Pro Solutions?',
        'Supprime 99% des virus, bactéries, chlore et particules organiques grâce à notre système 4 étapes.': 'Removes 99% of viruses, bacteria, chlorine and organic particles thanks to our 4-step system.',
        'Aucun électricien nécessaire! Installation rapide sans électricité, utilise uniquement la pression du réseau.': 'No electrician needed! Quick installation without electricity, uses only network pressure.',
        'Économisez 500-700€ par an en supprimant l\'achat de bouteilles d\'eau. Rentabilité en moins d\'un an.': 'Save €500-700 per year by eliminating bottled water purchases. Payback in less than one year.',
        'Systèmes haute capacité pour restaurants, bureaux et commerces. Jusqu\'à 500L/jour de production.': 'High capacity systems for restaurants, offices and businesses. Up to 500L/day production.',
        'Surveillance en temps réel de la qualité, alerts automatiques et maintenance prédictive incluse.': 'Real-time quality monitoring, automatic alerts and predictive maintenance included.',
        'Installation professionnelle, formation personnel et maintenance 24/7 avec techniciens certifiés.': 'Professional installation, staff training and 24/7 maintenance with certified technicians.',
        'Eau Pure avec Système d\'Osmose Inverse': 'Pure Water with Reverse Osmosis System',
        'Eliminez 99% des contaminants avec notre technologie avancée': 'Eliminate 99% of contaminants with our advanced technology',
        'Commander Maintenant': 'Order Now',
        'Garantie 2 ans': '2-year warranty',
        'Installation incluse': 'Installation included',
        'SAV France': 'French Support',
        '99% Contaminants éliminés': '99% Contaminants eliminated'
      },
      'es': {
        'Élimination Totale': 'Eliminación Total',
        'Installation Simple': 'Instalación Simple',
        'Économies Garanties': 'Ahorros Garantizados', 
        'Capacité Industrielle': 'Capacidad Industrial',
        'Monitoring Avancé': 'Monitoreo Avanzado',
        'Support Dédié': 'Soporte Dedicado',
        'Pourquoi Choisir Nos Systèmes?': '¿Por Qué Elegir Nuestros Sistemas?',
        'Pourquoi Choisir Nos Solutions Pro?': '¿Por Qué Elegir Nuestras Soluciones Pro?'
      },
      'de': {
        'Élimination Totale': 'Vollständige Elimination',
        'Installation Simple': 'Einfache Installation',
        'Économies Garanties': 'Garantierte Einsparungen',
        'Capacité Industrielle': 'Industrielle Kapazität', 
        'Monitoring Avancé': 'Erweiterte Überwachung',
        'Support Dédié': 'Dedizierter Support',
        'Pourquoi Choisir Nos Systèmes?': 'Warum Unsere Systeme Wählen?',
        'Pourquoi Choisir Nos Solutions Pro?': 'Warum Unsere Pro-Lösungen Wählen?'
      }
    };

    const translations = hardcodedTranslations[targetLanguage] || {};
    
    // Apply hardcoded translations immediately
    for (const [french, translated] of Object.entries(translations)) {
      await this.replaceTextOnPage(french, translated);
    }
  }

  async replaceTextOnPage(originalText, translatedText) {
    const walker = document.createTreeWalker(
      document.body,
      NodeFilter.SHOW_TEXT,
      null,
      false
    );

    const textNodes = [];
    let node;
    
    while ((node = walker.nextNode())) {
      if (node.nodeValue && node.nodeValue.includes(originalText)) {
        textNodes.push(node);
      }
    }

    textNodes.forEach(textNode => {
      try {
        // Vérifier que le node a encore un parent avant de le modifier
        if (textNode.parentNode && textNode.nodeValue) {
          textNode.nodeValue = textNode.nodeValue.replace(new RegExp(originalText, 'g'), translatedText);
        }
      } catch (error) {
        console.warn('⚠️ Erreur lors du remplacement de texte:', error);
      }
    });

    console.log(`🔄 Replaced: "${originalText}" → "${translatedText}"`);
  }

  triggerLanguageChange(targetLanguage) {
    // Force React i18n update
    if (window.i18n && window.i18n.changeLanguage) {
      window.i18n.changeLanguage(targetLanguage === 'en' ? 'en' : 'fr');
    }
    
    // Force custom language change event
    const event = new CustomEvent('forceLanguageChange', {
      detail: { language: targetLanguage }
    });
    window.dispatchEvent(event);
    
    // Force DOM update
    document.documentElement.lang = targetLanguage === 'en' ? 'en' : 'fr';
  }

  async scanForUntranslatedContent(currentLanguage) {
    if (currentLanguage === 'fr') return; // French is default, no translation needed
    
    const suspiciousElements = this.findSuspiciousElements(currentLanguage);
    
    if (suspiciousElements.length > 0) {
      console.log(`🔍 Found ${suspiciousElements.length} potentially untranslated elements`);
      
      for (const element of suspiciousElements) {
        await this.translateElement(element, currentLanguage);
      }
      
      this.triggerReactUpdate();
    }
  }

  findAllTextElements() {
    const selectors = [
      'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
      'p', 'span', 'div[class*="text"]',
      'button', 'a',
      '[class*="title"]', '[class*="description"]',
      '[class*="content"]', '[class*="label"]'
    ];
    
    const elements = [];
    
    selectors.forEach(selector => {
      const found = document.querySelectorAll(selector);
      found.forEach(element => {
        if (this.hasTranslatableText(element)) {
          elements.push(element);
        }
      });
    });
    
    return elements;
  }

  findSuspiciousElements(currentLanguage) {
    // Look for French text when language is not French
    const frenchIndicators = [
      'pourquoi', 'choisir', 'nos', 'systèmes', 'système',
      'élimination', 'totale', 'supprime', 'grâce',
      'avec', 'notre', 'étapes', 'contaminants',
      'eau', 'pure', 'filtration', 'professionnelle',
      'garantie', 'installation', 'incluse'
    ];
    
    const suspiciousElements = [];
    const allTextElements = this.findAllTextElements();
    
    allTextElements.forEach(element => {
      const text = element.textContent.toLowerCase().trim();
      
      // Check if element contains French words when language is not French
      if (currentLanguage !== 'fr' && text.length > 3) {
        const containsFrench = frenchIndicators.some(indicator => 
          text.includes(indicator.toLowerCase())
        );
        
        if (containsFrench && !this.pendingElements.has(element)) {
          suspiciousElements.push(element);
          this.pendingElements.add(element);
        }
      }
    });
    
    return suspiciousElements;
  }

  hasTranslatableText(element) {
    const text = element.textContent.trim();
    
    // Skip if no text or too short
    if (!text || text.length < 3) return false;
    
    // Skip if only numbers, punctuation, or symbols
    if (!/[a-zA-ZàâäéèêëïîôöùûüÿçÀÂÄÉÈÊËÏÎÔÖÙÛÜŸÇ]/.test(text)) return false;
    
    // Skip navigation elements that should not be translated
    const skipClasses = ['nav', 'menu', 'logo', 'brand', 'copyright'];
    const elementClasses = element.className.toLowerCase();
    if (skipClasses.some(skipClass => elementClasses.includes(skipClass))) return false;
    
    return true;
  }

  async translateElement(element, targetLanguage) {
    try {
      // Vérifier que l'élément existe encore dans le DOM
      if (!element || !element.parentNode || !document.body.contains(element)) {
        this.pendingElements.delete(element);
        return;
      }

      const originalText = element.textContent ? element.textContent.trim() : '';
      if (!originalText) {
        this.pendingElements.delete(element);
        return;
      }
      
      // Check cache first
      const cacheKey = `${originalText}_${targetLanguage}`;
      if (this.translationCache[cacheKey]) {
        // Vérifier que l'élément existe encore avant de le modifier
        if (element.parentNode && document.body.contains(element)) {
          element.textContent = this.translationCache[cacheKey];
        }
        this.pendingElements.delete(element);
        return;
      }
      
      // Call translation API
      const response = await axios.post(`${this.backendUrl}/api/translate`, {
        text: originalText,
        target_language: this.mapLanguageCode(targetLanguage),
        source_language: 'FR'
      });
      
      if (response.data && response.data.translated_text) {
        const translatedText = response.data.translated_text;
        
        // Update element only if it still exists in DOM
        if (element.parentNode && document.body.contains(element)) {
          element.textContent = translatedText;
        }
        
        // Cache translation
        this.translationCache[cacheKey] = translatedText;
        
        // Remove from pending
        this.pendingElements.delete(element);
        
        console.log(`✅ Translated: "${originalText}" → "${translatedText}"`);
      }
      
    } catch (error) {
      console.error('❌ Translation failed for element:', error);
      this.pendingElements.delete(element);
    }
  }

  mapLanguageCode(i18nCode) {
    const mapping = {
      'en': 'EN-US',
      'es': 'ES',
      'de': 'DE',
      'it': 'IT',
      'pt': 'PT-BR',
      'fr': 'FR'
    };
    
    return mapping[i18nCode] || 'EN-US';
  }

  triggerReactUpdate() {
    // Dispatch custom event to trigger React re-renders
    const event = new CustomEvent('translationGuardianUpdate', {
      detail: { timestamp: Date.now() }
    });
    window.dispatchEvent(event);
  }

  // Public methods for manual control
  forceRetranslation() {
    const currentLanguage = window.i18n?.language || 'fr';
    this.forceCompleteRetranslation(currentLanguage);
  }

  pause() {
    this.isActive = false;
    console.log('⏸️ Translation Guardian paused');
  }

  resume() {
    this.isActive = true;
    console.log('▶️ Translation Guardian resumed');
  }

  getStatus() {
    return {
      isActive: this.isActive,
      currentLanguage: this.lastLanguage,
      cacheSize: Object.keys(this.translationCache).length,
      pendingElements: this.pendingElements.size,
      retryAttempts: this.retryAttempts
    };
  }
}

const TranslationGuardianComponent = () => {
  const { i18n } = useTranslation();
  const [guardianStatus, setGuardianStatus] = useState(null);
  const guardianRef = useRef(null);

  useEffect(() => {
    // Initialize Guardian
    if (!guardianRef.current) {
      guardianRef.current = new TranslationGuardian();
    }

    // Listen for language changes from i18n
    const handleLanguageChange = (lng) => {
      console.log('🌍 i18n language changed to:', lng);
      if (guardianRef.current) {
        setTimeout(() => {
          guardianRef.current.forceCompleteRetranslation(lng);
        }, 500); // Small delay to let i18n finish
      }
    };

    // Listen for guardian updates
    const handleGuardianUpdate = () => {
      if (guardianRef.current) {
        setGuardianStatus(guardianRef.current.getStatus());
      }
    };

    // Attach listeners
    i18n.on('languageChanged', handleLanguageChange);
    window.addEventListener('translationGuardianUpdate', handleGuardianUpdate);

    // Initial status
    setTimeout(() => handleGuardianUpdate(), 1000);

    return () => {
      i18n.off('languageChanged', handleLanguageChange);
      window.removeEventListener('translationGuardianUpdate', handleGuardianUpdate);
    };
  }, [i18n]);

  // Expose guardian globally for debugging
  useEffect(() => {
    if (guardianRef.current) {
      window.translationGuardian = guardianRef.current;
    }
  }, []);

  // Development UI (COMPLETEMENT SUPPRIME EN PRODUCTION)
  if (process.env.NODE_ENV === 'development' && process.env.REACT_APP_DEBUG_TRANSLATION && guardianStatus) {
    return (
      <div className="fixed bottom-20 right-4 bg-green-800 bg-opacity-90 text-white p-3 rounded-lg text-xs z-40 max-w-xs">
        <div className="font-bold mb-2">🛡️ Translation Guardian</div>
        <div>Status: {guardianStatus.isActive ? '✅ Active' : '⏸️ Paused'}</div>
        <div>Language: {guardianStatus.currentLanguage}</div>
        <div>Cache: {guardianStatus.cacheSize} translations</div>
        <div>Pending: {guardianStatus.pendingElements}</div>
        {guardianStatus.retryAttempts > 0 && (
          <div className="text-yellow-300">Retries: {guardianStatus.retryAttempts}</div>
        )}
      </div>
    );
  }

  return null;
};

export default TranslationGuardianComponent;