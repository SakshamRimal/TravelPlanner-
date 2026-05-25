import { createContext, useContext, useState, useEffect } from "react";

const STORAGE_KEY = "tp_app_state";

const defaultState = {
  selectedTrip: null,
  preferences: {},
  // Budget persistence
  budgetForm: { destination: "Pokhara", days: 3, travelers: 1 },
  budgetResult: null,
  budgetCurrency: "NPR",
  // Chat persistence
  chatMessages: [],
  chatSelectedTrip: null,
};

const AppStateContext = createContext();

export function AppStateProvider({ children }) {
  const [state, setState] = useState(() => {
    try {
      const stored = localStorage.getItem(STORAGE_KEY);
      if (!stored) return defaultState;
      // Merge so new keys are always present even after schema changes
      return { ...defaultState, ...JSON.parse(stored) };
    } catch {
      return defaultState;
    }
  });

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [state]);

  // Partial-merge updater — works like setState in class components
  const updateState = (partial) =>
    setState((prev) => ({ ...prev, ...partial }));

  return (
    <AppStateContext.Provider value={{ state, setState, updateState }}>
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
