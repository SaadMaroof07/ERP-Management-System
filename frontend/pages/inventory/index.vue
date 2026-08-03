<script setup lang="ts">
definePageMeta({ middleware: "auth" });

import { useAuthStore } from "~/stores/auth";

const auth = useAuthStore();
const api = useApi();
const products = ref<any[]>([]);
const count = ref(0);
const page = ref(1);
const search = ref("");
const loading = ref(false);
const errorMsg = ref("");
const confirmDeleteId = ref<number | null>(null);

const stockModal = ref<any>(null);
const stockForm = reactive({ movement_type: "in", quantity: 1, notes: "" });
const stockSaving = ref(false);
const stockError = ref("");

async function fetchProducts() {
  loading.value = true;
  try {
    const data: any = await api.get("/products/", { page: page.value, search: search.value || undefined });
    products.value = data.results;
    count.value = data.count;
  } finally {
    loading.value = false;
  }
}

let searchTimeout: any = null;
watch(search, () => { clearTimeout(searchTimeout); searchTimeout = setTimeout(() => { page.value = 1; fetchProducts(); }, 400); });
watch(page, fetchProducts);
onMounted(fetchProducts);

async function handleDelete(id: number) {
  try {
    await api.del(`/products/${id}/`);
    confirmDeleteId.value = null;
    fetchProducts();
  } catch {
    errorMsg.value = "Failed to delete product.";
  }
}

function openStockModal(product: any) {
  stockModal.value = product;
  stockForm.movement_type = "in";
  stockForm.quantity = 1;
  stockForm.notes = "";
  stockError.value = "";
}

async function submitStockMovement() {
  stockSaving.value = true;
  stockError.value = "";
  try {
    await api.post("/stock-movements/", {
      product: stockModal.value.id,
      movement_type: stockForm.movement_type,
      quantity: stockForm.quantity,
      notes: stockForm.notes,
    });
    stockModal.value = null;
    fetchProducts();
  } catch (e: any) {
    stockError.value = e?.data?.quantity?.[0] || e?.data?.detail || "Could not record stock movement.";
  } finally {
    stockSaving.value = false;
  }
}

const totalPages = computed(() => Math.max(1, Math.ceil(count.value / 10)));
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-bold text-slate-800">Inventory</h1>
      <NuxtLink v-if="auth.canManageInventory" to="/inventory/new" class="bg-slate-900 hover:bg-slate-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition">+ Add Product</NuxtLink>
    </div>

    <input v-model="search" placeholder="Search by name or SKU..." class="w-full border rounded-lg px-3 py-2 mb-4" />
    <p v-if="errorMsg" class="text-red-600 text-sm mb-3">{{ errorMsg }}</p>
    <p v-if="loading" class="text-slate-500 text-sm">Loading...</p>

    <div v-if="!loading && products.length" class="bg-white rounded-xl shadow overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-slate-100 text-left text-slate-600">
          <tr><th class="px-4 py-3">Name</th><th class="px-4 py-3">SKU</th><th class="px-4 py-3">Category</th><th class="px-4 py-3">Stock</th><th class="px-4 py-3">Price</th><th class="px-4 py-3 text-right">Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="p in products" :key="p.id" class="border-t hover:bg-slate-50">
            <td class="px-4 py-3 font-medium">{{ p.name }}</td>
            <td class="px-4 py-3 text-slate-500">{{ p.sku }}</td>
            <td class="px-4 py-3">{{ p.category_name || "—" }}</td>
            <td class="px-4 py-3">
              <span :class="p.is_low_stock ? 'text-red-600 font-semibold' : ''">{{ p.quantity_in_stock }} {{ p.unit }}</span>
              <span v-if="p.is_low_stock" class="ml-1 text-xs bg-red-100 text-red-700 px-1.5 py-0.5 rounded-full">Low</span>
            </td>
            <td class="px-4 py-3">Rs {{ Number(p.unit_price).toLocaleString() }}</td>
            <td class="px-4 py-3 text-right space-x-2">
              <button v-if="auth.canManageInventory" class="text-emerald-600 hover:underline" @click="openStockModal(p)">Adjust Stock</button>
              <NuxtLink v-if="auth.canManageInventory" :to="`/inventory/${p.id}`" class="text-slate-900 hover:underline">Edit</NuxtLink>
              <button v-if="auth.isAdmin" class="text-red-600 hover:underline" @click="confirmDeleteId = p.id">Delete</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-if="!loading && count > 10" class="flex justify-center items-center gap-3 mt-6 text-sm">
      <button :disabled="page === 1" class="px-3 py-1 rounded border disabled:opacity-40" @click="page--">Prev</button>
      <span>Page {{ page }} of {{ totalPages }}</span>
      <button :disabled="page >= totalPages" class="px-3 py-1 rounded border disabled:opacity-40" @click="page++">Next</button>
    </div>

    <!-- Delete confirmation -->
    <div v-if="confirmDeleteId" class="fixed inset-0 bg-black/40 flex items-center justify-center px-4 z-50">
      <div class="bg-white rounded-xl p-6 max-w-sm w-full">
        <p class="font-medium mb-4">Delete this product? This cannot be undone.</p>
        <div class="flex justify-end gap-3">
          <button class="px-4 py-2 rounded border" @click="confirmDeleteId = null">Cancel</button>
          <button class="px-4 py-2 rounded bg-red-600 text-white" @click="handleDelete(confirmDeleteId)">Delete</button>
        </div>
      </div>
    </div>

    <!-- Stock adjustment modal -->
    <div v-if="stockModal" class="fixed inset-0 bg-black/40 flex items-center justify-center px-4 z-50">
      <form class="bg-white rounded-xl p-6 max-w-sm w-full space-y-3" @submit.prevent="submitStockMovement">
        <h2 class="font-semibold">Adjust Stock — {{ stockModal.name }}</h2>
        <p class="text-xs text-slate-500">Current stock: {{ stockModal.quantity_in_stock }} {{ stockModal.unit }}</p>

        <select v-model="stockForm.movement_type" class="w-full border rounded-lg px-3 py-2 text-sm">
          <option value="in">Stock In (receive)</option>
          <option value="out">Stock Out (remove)</option>
          <option value="adjustment">Manual Adjustment (+/-)</option>
        </select>
        <input v-model.number="stockForm.quantity" type="number" required class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="Quantity" />
        <input v-model="stockForm.notes" class="w-full border rounded-lg px-3 py-2 text-sm" placeholder="Notes (optional)" />

        <p v-if="stockError" class="text-sm text-red-600">{{ stockError }}</p>

        <div class="flex gap-3 pt-1">
          <button type="submit" :disabled="stockSaving" class="bg-slate-900 hover:bg-slate-700 disabled:opacity-60 text-white text-sm font-medium px-4 py-2 rounded-lg transition">
            {{ stockSaving ? "Saving..." : "Save" }}
          </button>
          <button type="button" class="px-4 py-2 rounded-lg border text-sm" @click="stockModal = null">Cancel</button>
        </div>
      </form>
    </div>
  </div>
</template>
