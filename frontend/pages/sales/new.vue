<script setup lang="ts">
definePageMeta({ middleware: "auth" });

const api = useApi();
const router = useRouter();

const products = ref<any[]>([]);
const customers = ref<any[]>([]);
const search = ref("");
const cart = reactive<any[]>([]);
const customerId = ref<number | null>(null);
const notes = ref("");
const loading = ref(false);
const errorMsg = ref("");

async function searchProducts() {
  const data: any = await api.get("/products/", { search: search.value || undefined, is_active: true });
  products.value = data.results;
}

onMounted(async () => {
  searchProducts();
  const c: any = await api.get("/customers/");
  customers.value = c.results || c;
});

let searchTimeout: any = null;
watch(search, () => { clearTimeout(searchTimeout); searchTimeout = setTimeout(searchProducts, 400); });

function addToCart(product: any) {
  const existing = cart.find((i) => i.product === product.id);
  if (existing) {
    existing.quantity++;
  } else {
    cart.push({ product: product.id, name: product.name, unit_price: product.unit_price, quantity: 1, max: product.quantity_in_stock });
  }
}

function removeFromCart(index: number) {
  cart.splice(index, 1);
}

const total = computed(() => cart.reduce((sum, i) => sum + i.unit_price * i.quantity, 0));

async function handleCheckout() {
  if (!cart.length) {
    errorMsg.value = "Add at least one product to the sale.";
    return;
  }
  loading.value = true;
  errorMsg.value = "";
  try {
    const sale: any = await api.post("/sales/checkout/", {
      customer: customerId.value,
      notes: notes.value,
      items: cart.map((i) => ({ product: i.product, quantity: i.quantity })),
    });
    router.push("/sales");
  } catch (e: any) {
    errorMsg.value = e?.data?.detail || "Checkout failed.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div>
    <h1 class="text-xl font-bold text-slate-800 mb-6">New Sale</h1>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div class="lg:col-span-2">
        <input v-model="search" placeholder="Search products..." class="w-full border rounded-lg px-3 py-2 mb-4" />
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-3">
          <button
            v-for="p in products" :key="p.id" type="button"
            :disabled="p.quantity_in_stock === 0"
            class="bg-white rounded-xl shadow p-3 text-left disabled:opacity-40 hover:shadow-md transition"
            @click="addToCart(p)"
          >
            <p class="font-medium text-sm">{{ p.name }}</p>
            <p class="text-xs text-slate-500">{{ p.sku }}</p>
            <p class="text-sm font-semibold text-emerald-700 mt-1">Rs {{ Number(p.unit_price).toLocaleString() }}</p>
            <p class="text-xs text-slate-400">Stock: {{ p.quantity_in_stock }}</p>
          </button>
        </div>
      </div>

      <div class="bg-white rounded-xl shadow p-4 h-fit">
        <h2 class="font-semibold mb-3">Cart</h2>

        <select v-model="customerId" class="w-full border rounded-lg px-3 py-2 text-sm mb-3">
          <option :value="null">Walk-in customer</option>
          <option v-for="c in customers" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>

        <p v-if="!cart.length" class="text-sm text-slate-400">No items added yet.</p>

        <div v-for="(item, idx) in cart" :key="item.product" class="flex items-center justify-between text-sm py-1.5 border-b">
          <div>
            <p>{{ item.name }}</p>
            <p class="text-xs text-slate-500">Rs {{ Number(item.unit_price).toLocaleString() }} × {{ item.quantity }}</p>
          </div>
          <div class="flex items-center gap-2">
            <input v-model.number="item.quantity" type="number" min="1" :max="item.max" class="w-14 border rounded px-1 py-0.5 text-center" />
            <button class="text-red-600" @click="removeFromCart(idx)">✕</button>
          </div>
        </div>

        <div class="flex justify-between font-bold pt-3 mt-2 border-t">
          <span>Total</span>
          <span class="text-emerald-700">Rs {{ Number(total).toLocaleString() }}</span>
        </div>

        <input v-model="notes" placeholder="Notes (optional)" class="w-full border rounded-lg px-3 py-2 text-sm mt-3" />

        <p v-if="errorMsg" class="text-sm text-red-600 mt-2">{{ errorMsg }}</p>

        <button :disabled="loading" class="w-full bg-slate-900 hover:bg-slate-700 disabled:opacity-60 text-white font-medium py-2.5 rounded-lg transition mt-3" @click="handleCheckout">
          {{ loading ? "Processing..." : "Complete Sale" }}
        </button>
      </div>
    </div>
  </div>
</template>
