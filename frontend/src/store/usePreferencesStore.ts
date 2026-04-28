import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { CardNetwork } from '../features/transactions/types';

type PreferencesStore = {
  preferredCurrency: string;
  preferredCardNetwork: CardNetwork;

  setPreferredCurrency: (currency: string) => void;
  setPreferredCardNetwork: (cardNetwork: CardNetwork) => void;
};

export const usePreferencesStore = create<PreferencesStore>()(
  persist(
    (set) => ({
      preferredCurrency: 'USD',
      preferredCardNetwork: 'visa',

      setPreferredCurrency: (currency) => {
        set({ preferredCurrency: currency });
      },

      setPreferredCardNetwork: (cardNetwork) => {
        set({ preferredCardNetwork: cardNetwork });
      },
    }),
    {
      name: 'schemeguard-preferences',
      partialize: (state) => ({
        preferredCurrency: state.preferredCurrency,
        preferredCardNetwork: state.preferredCardNetwork,
      }),
    },
  ),
);