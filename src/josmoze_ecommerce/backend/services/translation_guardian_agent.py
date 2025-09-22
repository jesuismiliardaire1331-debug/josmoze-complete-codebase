#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Translation Guardian Agent - Backend
====================================
Agent IA spécialisé dans la surveillance et correction automatique des traductions.

Missions:
- Surveiller la cohérence des traductions
- Détecter les contenus non traduits
- Forcer la retraduction automatique
- Maintenir un cache de traductions optimisé
- Rapporter les problèmes de traduction

Auteur: Système OSMOSE v1.0
"""

import asyncio
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
import re
from translation_service import translation_service

class TranslationGuardianAgent:
    """Agent gardien des traductions - surveillance et correction automatique"""
    
    def __init__(self):
        self.is_active = True
        self.translation_cache = {}
        self.problematic_translations = {}
        self.language_patterns = self._init_language_patterns()
        self.check_interval = 30  # Check every 30 seconds
        self.last_check = datetime.now()
        self.stats = {
            'translations_fixed': 0,
            'cache_hits': 0,
            'api_calls': 0,
            'problems_detected': 0,
            'uptime': datetime.now()
        }
        
        logging.info("🛡️ Translation Guardian Agent initialized")
        
    def _init_language_patterns(self) -> Dict[str, List[str]]:
        """Initialize language detection patterns"""
        return {
            'french': [
                r'\b(le|la|les|un|une|des|du|de|pour|avec|dans|sur|par|sans|mais|ou|et|donc|or|ni|car)\b',
                r'\b(pourquoi|comment|quand|où|qui|que|quoi)\b',
                r'\b(bonjour|salut|merci|s\'il vous plaît|au revoir)\b',
                r'\b(système|systèmes|élimination|contaminants|garantie)\b'
            ],
            'english': [
                r'\b(the|a|an|and|or|but|for|with|in|on|at|by|from)\b',
                r'\b(why|how|when|where|who|what)\b',
                r'\b(hello|hi|thank you|please|goodbye)\b',
                r'\b(system|systems|elimination|contaminants|warranty)\b'
            ],
            'spanish': [
                r'\b(el|la|los|las|un|una|y|o|pero|para|con|en|por)\b',
                r'\b(por qué|cómo|cuándo|dónde|quién|qué)\b',
                r'\b(hola|gracias|por favor|adiós)\b',
                r'\b(sistema|sistemas|eliminación|contaminantes|garantía)\b'
            ],
            'german': [
                r'\b(der|die|das|ein|eine|und|oder|aber|für|mit|in|auf)\b',
                r'\b(warum|wie|wann|wo|wer|was)\b',
                r'\b(hallo|danke|bitte|auf wiedersehen)\b',
                r'\b(system|systeme|elimination|schadstoffe|garantie)\b'
            ]
        }
    
    def detect_language(self, text: str) -> Optional[str]:
        """Detect the language of given text"""
        if not text or len(text.strip()) < 3:
            return None
            
        text_lower = text.lower()
        scores = {}
        
        for language, patterns in self.language_patterns.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, text_lower, re.IGNORECASE)
                score += len(matches)
            scores[language] = score
        
        if not scores or max(scores.values()) == 0:
            return None
            
        detected_language = max(scores, key=scores.get)
        return detected_language
    
    async def check_translation_consistency(self, content: Dict, expected_language: str) -> Dict:
        """Check if content is consistently translated to expected language"""
        issues = []
        fixes_applied = 0
        
        for key, text in content.items():
            if not isinstance(text, str) or len(text.strip()) < 3:
                continue
                
            detected = self.detect_language(text)
            
            if detected and detected != expected_language.lower():
                # Language mismatch detected
                issue = {
                    'key': key,
                    'text': text,
                    'expected_language': expected_language,
                    'detected_language': detected,
                    'severity': 'high' if len(text) > 50 else 'medium'
                }
                issues.append(issue)
                
                # Try to fix automatically
                corrected_text = await self._auto_correct_translation(text, expected_language)
                if corrected_text and corrected_text != text:
                    content[key] = corrected_text
                    fixes_applied += 1
                    logging.info(f"✅ Auto-corrected translation: {key}")
        
        self.stats['problems_detected'] += len(issues)
        self.stats['translations_fixed'] += fixes_applied
        
        return {
            'issues_found': len(issues),
            'fixes_applied': fixes_applied,
            'issues': issues,
            'corrected_content': content
        }
    
    async def _auto_correct_translation(self, text: str, target_language: str) -> Optional[str]:
        """Attempt to automatically correct a mistranslated text"""
        try:
            # Check cache first
            cache_key = f"{text}_{target_language}"
            if cache_key in self.translation_cache:
                self.stats['cache_hits'] += 1
                return self.translation_cache[cache_key]
            
            # Map language codes
            deepl_language_map = {
                'english': 'EN-US',
                'spanish': 'ES',
                'german': 'DE',
                'french': 'FR'
            }
            
            deepl_code = deepl_language_map.get(target_language.lower(), 'EN-US')
            
            # Call translation service
            result = await translation_service.translate_text(
                text=text,
                target_language=deepl_code,
                source_language='FR'
            )
            
            if result and 'translated_text' in result:
                translated_text = result['translated_text']
                
                # Cache the result
                self.translation_cache[cache_key] = translated_text
                self.stats['api_calls'] += 1
                
                return translated_text
                
        except Exception as e:
            logging.error(f"❌ Auto-correction failed: {e}")
            self.problematic_translations[text] = str(e)
        
        return None
    
    async def force_retranslation(self, content_dict: Dict, target_language: str) -> Dict:
        """Force complete retranslation of content dictionary"""
        logging.info(f"🔄 Forcing complete retranslation to {target_language}")
        
        translated_content = {}
        
        for key, text in content_dict.items():
            if isinstance(text, str) and len(text.strip()) > 2:
                corrected = await self._auto_correct_translation(text, target_language)
                translated_content[key] = corrected if corrected else text
            else:
                translated_content[key] = text
        
        return translated_content
    
    def get_problematic_translations(self) -> Dict:
        """Get list of problematic translations that couldn't be fixed"""
        return self.problematic_translations
    
    def clear_cache(self) -> int:
        """Clear translation cache and return number of entries cleared"""
        cache_size = len(self.translation_cache)
        self.translation_cache.clear()
        logging.info(f"🧹 Translation cache cleared: {cache_size} entries removed")
        return cache_size
    
    def get_stats(self) -> Dict:
        """Get agent statistics"""
        uptime = datetime.now() - self.stats['uptime']
        return {
            **self.stats,
            'uptime_hours': uptime.total_seconds() / 3600,
            'cache_size': len(self.translation_cache),
            'problematic_count': len(self.problematic_translations),
            'last_check': self.last_check.isoformat()
        }
    
    async def periodic_check(self):
        """Periodic check for translation issues - run in background"""
        while self.is_active:
            try:
                current_time = datetime.now()
                
                # Perform maintenance tasks
                if (current_time - self.last_check).seconds > self.check_interval:
                    await self._perform_maintenance()
                    self.last_check = current_time
                
                await asyncio.sleep(self.check_interval)
                
            except Exception as e:
                logging.error(f"❌ Translation Guardian periodic check error: {e}")
                await asyncio.sleep(60)  # Wait longer on error
    
    async def _perform_maintenance(self):
        """Perform maintenance tasks"""
        # Clean old cache entries (older than 1 hour)
        current_time = time.time()
        cache_keys_to_remove = []
        
        # Simple cache cleanup (in production, you'd want timestamps)
        if len(self.translation_cache) > 1000:
            # Remove 10% oldest entries (simplified)
            keys_to_remove = list(self.translation_cache.keys())[:100]
            for key in keys_to_remove:
                del self.translation_cache[key]
            logging.info(f"🧹 Cache cleanup: removed {len(keys_to_remove)} entries")
        
        # Clear old problematic translations
        if len(self.problematic_translations) > 50:
            self.problematic_translations.clear()
            logging.info("🧹 Cleared problematic translations list")
    
    def stop(self):
        """Stop the guardian agent"""
        self.is_active = False
        logging.info("⏹️ Translation Guardian Agent stopped")

# Global instance
translation_guardian = TranslationGuardianAgent()

async def get_translation_guardian():
    """Get the global translation guardian instance"""
    return translation_guardian

async def start_translation_guardian_task():
    """Start the translation guardian background task"""
    asyncio.create_task(translation_guardian.periodic_check())
    logging.info("🚀 Translation Guardian background task started")

# Quick access functions
async def check_content_translation(content: Dict, language: str):
    """Quick function to check content translation"""
    return await translation_guardian.check_translation_consistency(content, language)

async def force_content_retranslation(content: Dict, language: str):
    """Quick function to force content retranslation"""
    return await translation_guardian.force_retranslation(content, language)

def get_guardian_stats():
    """Quick function to get guardian statistics"""
    return translation_guardian.get_stats()