import { defineStore } from "pinia";

interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role: string;
  is_staff: boolean;
}

export const useAuthStore = defineStore("auth", {
  state: () => ({
    access: null as string | null,
    refresh: null as string | null,
    user: null as User | null,
  }),

  getters: {
    isLoggedIn: (state) => !!state.access,
    isAdmin: (state) => state.user?.role === "admin" || state.user?.is_staff,
    isManagerOrAdmin: (state) => ["admin", "manager"].includes(state.user?.role || ""),
    canManageInventory: (state) => ["admin", "inventory"].includes(state.user?.role || ""),
    canManageSales: (state) => ["admin", "sales"].includes(state.user?.role || ""),
  },

  actions: {
    setTokens(access: string, refresh: string) {
      this.access = access;
      this.refresh = refresh;
      if (import.meta.client) {
        localStorage.setItem("erp_access", access);
        localStorage.setItem("erp_refresh", refresh);
      }
    },
    setUser(user: User) {
      this.user = user;
    },
    loadFromStorage() {
      if (import.meta.client) {
        this.access = localStorage.getItem("erp_access");
        this.refresh = localStorage.getItem("erp_refresh");
      }
    },
    logout() {
      this.access = null;
      this.refresh = null;
      this.user = null;
      if (import.meta.client) {
        localStorage.removeItem("erp_access");
        localStorage.removeItem("erp_refresh");
      }
    },
  },
});
