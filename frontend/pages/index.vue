<script setup lang="ts">
definePageMeta({ middleware: "auth" });

import { useAuthStore } from "~/stores/auth";

const auth = useAuthStore();
const api = useApi();
const stats = ref<any>(null);
const loading = ref(true);
const errorMsg = ref("");

onMounted(async () => {
  if (!auth.user) {
    try {
      const me = await api.get("/auth/me/");
      auth.setUser(me as any);
    } catch { /* handled by interceptor */ }
  }
  if (auth.isManagerOrAdmin) {
    try {
      stats.value = await api.get("/reports/dashboard/");
    } catch {
      errorMsg.value = "Could not load dashboard stats.";
    }
  }
  loading.value = false;
});
</script>

<template>
  <div>
    <h1 class="text-xl font-bold text-slate-800 mb-1">Welcome, {{ auth.user?.first_name || auth.user?.username }}</h1>
    <p class="text-sm text-slate-500 mb-6 capitalize">Role: {{ auth.user?.role }}</p>

    <div v-if="!auth.isManagerOrAdmin" class="bg-white rounded-xl shadow p-6">
      <p class="text-slate-600">Use the sidebar to access the modules available to your role.</p>
    </div>

    <p v-if="loading" class="text-slate-500 text-sm">Loading...</p>
    <p v-if="errorMsg" class="text-red-600 text-sm">{{ errorMsg }}</p>

    <div v-if="stats" class="grid grid-cols-2 lg:grid-cols-3 gap-4">
      <div class="bg-white rounded-xl shadow p-4">
        <p class="text-xs text-slate-500">Active Employees</p>
        <p class="text-2xl font-bold mt-1">{{ stats.total_employees }}</p>
      </div>
      <div class="bg-white rounded-xl shadow p-4">
        <p class="text-xs text-slate-500">Active Products</p>
        <p class="text-2xl font-bold mt-1">{{ stats.total_products }}</p>
      </div>
      <div class="bg-white rounded-xl shadow p-4">
        <p class="text-xs text-slate-500">Low Stock Items</p>
        <p class="text-2xl font-bold mt-1" :class="stats.low_stock_count > 0 ? 'text-red-600' : ''">{{ stats.low_stock_count }}</p>
      </div>
      <div class="bg-white rounded-xl shadow p-4">
        <p class="text-xs text-slate-500">Completed Sales</p>
        <p class="text-2xl font-bold mt-1">{{ stats.total_sales_count }}</p>
      </div>
      <div class="bg-white rounded-xl shadow p-4">
        <p class="text-xs text-slate-500">Sales Revenue</p>
        <p class="text-2xl font-bold mt-1 text-emerald-700">Rs {{ Number(stats.total_sales_amount).toLocaleString() }}</p>
      </div>
      <div class="bg-white rounded-xl shadow p-4">
        <p class="text-xs text-slate-500">Inventory Value</p>
        <p class="text-2xl font-bold mt-1">Rs {{ Number(stats.inventory_value).toLocaleString() }}</p>
      </div>
    </div>
  </div>
</template>
