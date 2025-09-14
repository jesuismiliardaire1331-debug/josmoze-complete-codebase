import { useRef, useEffect } from 'react';

/**
 * Hook for safe cleanup in React 18 StrictMode
 * Prevents double cleanup errors
 */
export const useSafeCleanup = () => {
  const mountedRef = useRef(true);
  const timeoutsRef = useRef(new Set());
  const intervalsRef = useRef(new Set());

  const safeSetTimeout = (callback, delay) => {
    const timeoutId = setTimeout(() => {
      if (mountedRef.current) {
        timeoutsRef.current.delete(timeoutId);
        callback();
      }
    }, delay);
    
    timeoutsRef.current.add(timeoutId);
    return timeoutId;
  };

  const safeClearTimeout = (timeoutId) => {
    if (timeoutsRef.current.has(timeoutId)) {
      clearTimeout(timeoutId);
      timeoutsRef.current.delete(timeoutId);
    }
  };

  const safeSetInterval = (callback, delay) => {
    const intervalId = setInterval(() => {
      if (mountedRef.current) {
        callback();
      } else {
        safeClearInterval(intervalId);
      }
    }, delay);
    
    intervalsRef.current.add(intervalId);
    return intervalId;
  };

  const safeClearInterval = (intervalId) => {
    if (intervalsRef.current.has(intervalId)) {
      clearInterval(intervalId);
      intervalsRef.current.delete(intervalId);
    }
  };

  const isMounted = () => mountedRef.current;

  useEffect(() => {
    return () => {
      mountedRef.current = false;
      
      // Clear all timeouts
      timeoutsRef.current.forEach(timeoutId => {
        clearTimeout(timeoutId);
      });
      timeoutsRef.current.clear();
      
      // Clear all intervals
      intervalsRef.current.forEach(intervalId => {
        clearInterval(intervalId);
      });
      intervalsRef.current.clear();
    };
  }, []);

  return {
    safeSetTimeout,
    safeClearTimeout,
    safeSetInterval,
    safeClearInterval,
    isMounted
  };
};

export default useSafeCleanup;