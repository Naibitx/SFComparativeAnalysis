import { useState, useEffect, useCallback, useRef } from 'react';

/** Generic data-fetching hook.*/
export function useAsync(fetchFn, deps = []) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await fetchFn();
      setData(result);
    } catch (e) {
      setError(e.message || 'Unknown error');
    } finally {
      setLoading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps);

  useEffect(() => { load(); }, [load]);

  return { data, loading, error, refetch: load };
}

/**polling hook calls fetchFn every `intervalMs` until `shouldStop` returns true.*/
export function usePolling(fetchFn, intervalMs = 2000, shouldStop = () => false) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const timerRef = useRef(null);

  const poll = useCallback(async () => {
    try {
      const result = await fetchFn();
      setData(result);
      setLoading(false);
      if (shouldStop(result)) {
        clearInterval(timerRef.current);
      }
    } catch (e) {
      setError(e.message);
      setLoading(false);
      clearInterval(timerRef.current);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    poll();
    timerRef.current = setInterval(poll, intervalMs);
    return () => clearInterval(timerRef.current);
  }, [poll, intervalMs]);

  return { data, loading, error };
}
