<script setup lang="ts">
const props = defineProps<{
  modelValue: Record<string, any>;
  categories: { id: number; name: string }[];
  submitLabel: string;
  loading: boolean;
  errorMsg: string;
}>();
const emit = defineEmits(["submit"]);
const form = reactive({ ...props.modelValue });
</script>

<template>
  <form class="bg-white rounded-xl shadow p-6 space-y-4 max-w-2xl" @submit.prevent="emit('submit', form)">
    <div><label class="block text-sm font-medium mb-1">Name</label><input v-model="form.name" required class="w-full border rounded-lg px-3 py-2" /></div>
    <div><label class="block text-sm font-medium mb-1">Description</label><textarea v-model="form.description" rows="2" class="w-full border rounded-lg px-3 py-2"></textarea></div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div><label class="block text-sm font-medium mb-1">SKU</label><input v-model="form.sku" required class="w-full border rounded-lg px-3 py-2" /></div>
      <div>
        <label class="block text-sm font-medium mb-1">Category</label>
        <select v-model="form.category" class="w-full border rounded-lg px-3 py-2">
          <option :value="null">— None —</option>
          <option v-for="c in categories" :key="c.id" :value="c.id">{{ c.name }}</option>
        </select>
      </div>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
      <div><label class="block text-sm font-medium mb-1">Cost Price</label><input v-model.number="form.cost_price" type="number" min="0" step="0.01" required class="w-full border rounded-lg px-3 py-2" /></div>
      <div><label class="block text-sm font-medium mb-1">Selling Price</label><input v-model.number="form.unit_price" type="number" min="0" step="0.01" required class="w-full border rounded-lg px-3 py-2" /></div>
      <div><label class="block text-sm font-medium mb-1">Unit</label><input v-model="form.unit" placeholder="pcs" class="w-full border rounded-lg px-3 py-2" /></div>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div v-if="form.id"><label class="block text-sm font-medium mb-1">Current Stock</label><input :value="form.quantity_in_stock" disabled class="w-full border rounded-lg px-3 py-2 bg-slate-100 text-slate-500" /></div>
      <div><label class="block text-sm font-medium mb-1">Reorder Level</label><input v-model.number="form.reorder_level" type="number" min="0" required class="w-full border rounded-lg px-3 py-2" /></div>
    </div>
    <label class="flex items-center gap-2 text-sm"><input v-model="form.is_active" type="checkbox" /> Active</label>

    <p v-if="errorMsg" class="text-sm text-red-600">{{ errorMsg }}</p>

    <div class="flex gap-3 pt-2">
      <button type="submit" :disabled="loading" class="bg-slate-900 hover:bg-slate-700 disabled:opacity-60 text-white font-medium px-5 py-2 rounded-lg transition">
        {{ loading ? "Saving..." : submitLabel }}
      </button>
      <NuxtLink to="/inventory" class="px-5 py-2 rounded-lg border">Cancel</NuxtLink>
    </div>
  </form>
</template>
