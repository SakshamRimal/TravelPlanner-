import { useState, useEffect, useCallback } from 'react';
import { IconCheck, IconX, IconAlertCircle } from '@tabler/icons-react';

let toastId = 0;
let addToastFn = null;

export function showToast(message, type = 'success') {
  if (addToastFn) {
    addToastFn({ id: ++toastId, message, type });
  }
}

export function ToastContainer() {
  const [toasts, setToasts] = useState([]);

  const addToast = useCallback((toast) => {
    setToasts((prev) => [...prev, toast]);
  }, []);

  useEffect(() => {
    addToastFn = addToast;
    return () => {
      addToastFn = null;
    };
  }, [addToast]);

  useEffect(() => {
    if (toasts.length === 0) return;
    const timer = setTimeout(() => {
      setToasts((prev) => prev.slice(1));
    }, 3500);
    return () => clearTimeout(timer);
  }, [toasts]);

  if (toasts.length === 0) return null;

  return (
    <div className="toast-container">
      {toasts.map((toast) => (
        <div key={toast.id} className={`toast toast-${toast.type}`}>
          <div className="toast-icon">
            {toast.type === 'success' ? (
              <IconCheck size={18} />
            ) : (
              <IconAlertCircle size={18} />
            )}
          </div>
          <span className="toast-message">{toast.message}</span>
        </div>
      ))}
    </div>
  );
}