/**
 * DOM Utilities - React 18 Safe DOM manipulation
 * Prevents removeChild errors in StrictMode
 */

/**
 * Safely remove a DOM node
 * @param {Node} node - The node to remove
 */
export const safeRemoveNode = (node) => {
  try {
    if (node && node.parentNode && node.parentNode.contains(node)) {
      node.parentNode.removeChild(node);
      return true;
    }
  } catch (error) {
    console.warn('⚠️ Safe removal failed:', error);
  }
  return false;
};

/**
 * Safely append a node
 * @param {Node} parent - Parent node
 * @param {Node} child - Child node to append
 */
export const safeAppendChild = (parent, child) => {
  try {
    if (parent && child && !parent.contains(child)) {
      parent.appendChild(child);
      return true;
    }
  } catch (error) {
    console.warn('⚠️ Safe append failed:', error);
  }
  return false;
};

/**
 * Safely modify text content
 * @param {Element} element - Element to modify
 * @param {string} text - New text content
 */
export const safeSetTextContent = (element, text) => {
  try {
    if (element && element.parentNode && document.body.contains(element)) {
      element.textContent = text;
      return true;
    }
  } catch (error) {
    console.warn('⚠️ Safe text update failed:', error);
  }
  return false;
};

/**
 * Check if element is still in DOM
 * @param {Element} element - Element to check
 */
export const isElementInDOM = (element) => {
  return element && element.parentNode && document.body.contains(element);
};

/**
 * Safe timeout cleaner for React components
 */
export class SafeTimeout {
  constructor() {
    this.timeouts = new Set();
    this.isMounted = true;
  }

  setTimeout(callback, delay) {
    const timeoutId = setTimeout(() => {
      if (this.isMounted) {
        this.timeouts.delete(timeoutId);
        callback();
      }
    }, delay);
    
    this.timeouts.add(timeoutId);
    return timeoutId;
  }

  clearTimeout(timeoutId) {
    if (this.timeouts.has(timeoutId)) {
      clearTimeout(timeoutId);
      this.timeouts.delete(timeoutId);
    }
  }

  cleanup() {
    this.isMounted = false;
    this.timeouts.forEach(timeoutId => {
      clearTimeout(timeoutId);
    });
    this.timeouts.clear();
  }
}

export default {
  safeRemoveNode,
  safeAppendChild,
  safeSetTextContent,
  isElementInDOM,
  SafeTimeout
};