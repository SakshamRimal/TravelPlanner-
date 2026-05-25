import { createContext, useContext, useState, useEffect } from "react";

const STORAGE_KEY = "tp_app_state";

const defaultState = {
  // Add your global state fields here
  selectedTrip: null,
  preferences: {},
  // ...add more as needed
};

const AppStateContext = createContext();

export function AppStateProvider({ children }) {
  const [state, setState] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      return stored ? JSON.parse(stored) : defaultState;
    } catch {
      return defaultState;
    }
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [state]);

  return (
    <AppStateContext.Provider value={{ state, setState }}>
      {children}
    </AppStateContext.Provider>
  );
}

export function useAppState() {
  const context = useContext(AppStateContext);
  if (!context)
    throw new Error("useAppState must be used within AppStateProvider");
  return context;
}
