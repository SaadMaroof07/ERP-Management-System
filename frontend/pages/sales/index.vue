<script setup lang="ts">
definePageMeta({ middleware: "auth" });

import { useAuthStore } from "~/stores/auth";

const auth = useAuthStore();
const api = useApi();
const sales = ref<any[]>([]);
const loading = ref(true);
const cancellingId = ref<number | null>(null);

async function fetchSales() {
  loading.value = true;
  const data: any = await api.get("/sales/");
  sales.value = data.results || data;
  loading.value = false;
}
onMounted(fetchSales);

async function cancelSale(id: number) {
  cancellingId.value = id;
  try {
    await api.post(`/sales/${id}/cancel/`);
    fetchSales();
  } finally {
    cancellingId.value = null;
  }
}
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-bold text-slate-800">Sales</h1>
      <NuxtLink v-if="auth.canManageSales" to="/sales/new" class="bg-slate-900 hover:bg-slate-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition">+ New Sale</NuxtLink>
    </div>

    <p v-if="loading" class="text-slate-500 text-sm">Loading...</p>

    <div v-if="!loading && sales.length" class="bg-white rounded-xl shadow overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-slate-100 text-left text-slate-600">
          <tr><th class="px-4 py-3">Sale</th><th class="px-4 py-3">Customer</th><th class="px-4 py-3">Items</th><th class="px-4 py-3">Total</th><th class="px-4 py-3">Status</th><th class="px-4 py-3 text-right">Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="s in sales" :key="s.id" class="border-t hover:bg-slate-50">
            <td class="px-4 py-3">#{{ s.id }}</td>
            <td class="px-4 py-3">{{ s.customer_name || "Walk-in" }}</td>
            <td class="px-4 py-3">{{ s.items.length }} item(s)</td>
            <td class="px-4 py-3 font-semibold">Rs {{ Number(s.total_amount).toLocaleString() }}</td>
            <td class="px-4 py-3">
              <span class="px-2 py-0.5 rounded-full text-xs capitalize" :class="s.status === 'completed' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'">{{ s.status }}</span>
            </td>
            <td class="px-4 py-3 text-right">
              <button v-if="auth.canManageSales && s.status === 'completed'" :disabled="cancellingId === s.id" class="text-red-600 hover:underline text-sm" @click="cancelSale(s.id)">
                {{ cancellingId === s.id ? "Cancelling..." : "Cancel" }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
    <p v-if="!loading && !sales.length" class="text-slate-500 text-sm">No sales recorded yet.</p>
  </div>
</template>
