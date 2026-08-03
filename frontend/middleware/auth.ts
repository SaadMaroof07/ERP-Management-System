import { useAuthStore } from "~/stores/auth";

export default defineNuxtRouteMiddleware((to) => {
  const auth = useAuthStore();

  if (import.meta.client && !auth.access) {
    auth.loadFromStorage();
  }

  const publicPages = ["/login", "/register"];
  if (!auth.access && !publicPages.includes(to.path)) {
    return navigateTo("/login");
  }
});
