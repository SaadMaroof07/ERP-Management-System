<script setup lang="ts">
const props = defineProps<{
  modelValue: Record<string, any>;
  departments: { id: number; name: string }[];
  submitLabel: string;
  loading: boolean;
  errorMsg: string;
}>();
const emit = defineEmits(["submit"]);
const form = reactive({ ...props.modelValue });
</script>

<template>
  <form class="bg-white rounded-xl shadow p-6 space-y-4 max-w-2xl" @submit.prevent="emit('submit', form)">
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div><label class="block text-sm font-medium mb-1">First name</label><input v-model="form.first_name" required class="w-full border rounded-lg px-3 py-2" /></div>
      <div><label class="block text-sm font-medium mb-1">Last name</label><input v-model="form.last_name" required class="w-full border rounded-lg px-3 py-2" /></div>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div><label class="block text-sm font-medium mb-1">Email</label><input v-model="form.email" type="email" required class="w-full border rounded-lg px-3 py-2" /></div>
      <div><label class="block text-sm font-medium mb-1">Phone</label><input v-model="form.phone" required class="w-full border rounded-lg px-3 py-2" /></div>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div>
        <label class="block text-sm font-medium mb-1">Department</label>
        <select v-model="form.department" class="w-full border rounded-lg px-3 py-2">
          <option :value="null">— None —</option>
          <option v-for="d in departments" :key="d.id" :value="d.id">{{ d.name }}</option>
        </select>
      </div>
      <div><label class="block text-sm font-medium mb-1">Position</label><input v-model="form.position" required class="w-full border rounded-lg px-3 py-2" /></div>
    </div>
    <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
      <div><label class="block text-sm font-medium mb-1">Salary</label><input v-model.number="form.salary" type="number" min="0" step="0.01" required class="w-full border rounded-lg px-3 py-2" /></div>
      <div><label class="block text-sm font-medium mb-1">Hire date</label><input v-model="form.hire_date" type="date" required class="w-full border rounded-lg px-3 py-2" /></div>
    </div>
    <div>
      <label class="block text-sm font-medium mb-1">Status</label>
      <select v-model="form.status" class="w-full border rounded-lg px-3 py-2">
        <option value="active">Active</option>
        <option value="on_leave">On Leave</option>
        <option value="terminated">Terminated</option>
      </select>
    </div>

    <p v-if="errorMsg" class="text-sm text-red-600">{{ errorMsg }}</p>

    <div class="flex gap-3 pt-2">
      <button type="submit" :disabled="loading" class="bg-slate-900 hover:bg-slate-700 disabled:opacity-60 text-white font-medium px-5 py-2 rounded-lg transition">
        {{ loading ? "Saving..." : submitLabel }}
      </button>
      <NuxtLink to="/employees" class="px-5 py-2 rounded-lg border">Cancel</NuxtLink>
    </div>
  </form>
</template>
