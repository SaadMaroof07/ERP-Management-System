<script setup lang="ts">
import { useAuthStore } from "~/stores/auth";

const auth = useAuthStore();
const router = useRouter();
const menuOpen = ref(false);

onMounted(() => {
  auth.loadFromStorage();
});

function handleLogout() {
  auth.logout();
  router.push("/login");
}
</script>

<template>
  <div class="min-h-screen flex flex-col sm:flex-row" v-if="auth.isLoggedIn">
    <!-- Sidebar -->
    <aside class="bg-slate-900 text-white sm:w-56 sm:min-h-screen flex-shrink-0">
      <div class="p-4 flex items-center justify-between sm:block">
        <NuxtLink to="/" class="font-bold text-lg">Aptura ERP</NuxtLink>
        <button class="sm:hidden" @click="menuOpen = !menuOpen">☰</button>
      </div>
      <nav class="px-2 pb-4 space-y-1 text-sm" :class="menuOpen ? 'block' : 'hidden sm:block'">
        <NuxtLink to="/" class="block px-3 py-2 rounded hover:bg-slate-700">Dashboard</NuxtLink>
        <NuxtLink v-if="auth.isManagerOrAdmin" to="/employees" class="block px-3 py-2 rounded hover:bg-slate-700">Employees</NuxtLink>
        <NuxtLink to="/inventory" class="block px-3 py-2 rounded hover:bg-slate-700">Inventory</NuxtLink>
        <NuxtLink to="/sales" class="block px-3 py-2 rounded hover:bg-slate-700">Sales</NuxtLink>
        <NuxtLink v-if="auth.isManagerOrAdmin" to="/activity-logs" class="block px-3 py-2 rounded hover:bg-slate-700">Activity Logs</NuxtLink>
        <div class="border-t border-slate-700 mt-3 pt-3">
          <p class="px-3 text-xs text-slate-400">{{ auth.user?.username }} · {{ auth.user?.role }}</p>
          <button class="w-full text-left px-3 py-2 rounded hover:bg-slate-700 mt-1" @click="handleLogout">Logout</button>
        </div>
      </nav>
    </aside>

    <main class="flex-1 p-4 sm:p-6 max-w-6xl w-full mx-auto">
      <slot />
    </main>
  </div>

  <div v-else>
    <slot />
  </div>
</template>
