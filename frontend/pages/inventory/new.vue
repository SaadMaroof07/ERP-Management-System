<script setup lang="ts">
definePageMeta({ middleware: "auth" });

const api = useApi();
const router = useRouter();
const categories = ref<any[]>([]);
const loading = ref(false);
const errorMsg = ref("");
const blank = { name: "", description: "", sku: "", category: null, unit: "pcs", cost_price: 0, unit_price: 0, quantity_in_stock: 0, reorder_level: 10, is_active: true };

onMounted(async () => {
  const data: any = await api.get("/categories/");
  categories.value = data.results || data;
});

async function handleSubmit(form: any) {
  loading.value = true;
  errorMsg.value = "";
  try {
    await api.post("/products/", form);
    router.push("/inventory");
  } catch (e: any) {
    const data = e?.data;
    errorMsg.value = data ? Object.entries(data).map(([k, v]) => `${k}: ${v}`).join(" ") : "Failed to create product.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div>
    <h1 class="text-xl font-bold text-slate-800 mb-6">Add Product</h1>
    <ProductForm :model-value="blank" :categories="categories" submit-label="Create Product" :loading="loading" :error-msg="errorMsg" @submit="handleSubmit" />
  </div>
</template>
