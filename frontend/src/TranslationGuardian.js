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
    console.log('🚀 Forcing complete page retranslation to:', targetLanguage);
    
    try {
      // Get all text content on page
      const textElements = this.findAllTextElements();
      
      for (const element of textElements) {
        await this.translateElement(element, targetLanguage);
      }
      
      // Force React re-render
      this.triggerReactUpdate();
      
      console.log(`✅ Complete retranslation completed for ${textElements.length} elements`);
      
    } catch (error) {
      console.error('❌ Complete retranslation failed:', error);
      if (this.retryAttempts < this.maxRetries) {
        this.retryAttempts++;
        setTimeout(() => this.forceCompleteRetranslation(targetLanguage), 1000);
      }
    }
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
      const originalText = element.textContent.trim();
      
      // Check cache first
      const cacheKey = `${originalText}_${targetLanguage}`;
      if (this.translationCache[cacheKey]) {
        element.textContent = this.translationCache[cacheKey];
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
        
        // Update element
        element.textContent = translatedText;
        
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

  // Development UI (only show in development)
  if (process.env.NODE_ENV === 'development' && guardianStatus) {
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