<script setup lang="ts">
definePageMeta({ middleware: "auth" });

const api = useApi();
const router = useRouter();
const route = useRoute();
const categories = ref<any[]>([]);
const product = ref<any>(null);
const loading = ref(false);
const errorMsg = ref("");

onMounted(async () => {
  try {
    const [p, cats]: any = await Promise.all([api.get(`/products/${route.params.id}/`), api.get("/categories/")]);
    product.value = p;
    categories.value = cats.results || cats;
  } catch {
    errorMsg.value = "Could not load this product.";
  }
});

async function handleSubmit(form: any) {
  loading.value = true;
  errorMsg.value = "";
  try {
    await api.patch(`/products/${route.params.id}/`, form);
    router.push("/inventory");
  } catch (e: any) {
    const data = e?.data;
    errorMsg.value = data ? Object.entries(data).map(([k, v]) => `${k}: ${v}`).join(" ") : "Failed to update product.";
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <div>
    <h1 class="text-xl font-bold text-slate-800 mb-6">Edit Product</h1>
    <p v-if="errorMsg && !product" class="text-red-600 text-sm">{{ errorMsg }}</p>
    <ProductForm v-if="product" :model-value="product" :categories="categories" submit-label="Save Changes" :loading="loading" :error-msg="errorMsg" @submit="handleSubmit" />
  </div>
</template>
