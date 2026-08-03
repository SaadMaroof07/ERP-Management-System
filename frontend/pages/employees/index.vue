<script setup lang="ts">
definePageMeta({ middleware: "auth" });

const api = useApi();
const employees = ref<any[]>([]);
const count = ref(0);
const page = ref(1);
const search = ref("");
const loading = ref(false);
const confirmDeleteId = ref<number | null>(null);
const errorMsg = ref("");

async function fetchEmployees() {
  loading.value = true;
  try {
    const data: any = await api.get("/employees/", { page: page.value, search: search.value || undefined });
    employees.value = data.results;
    count.value = data.count;
  } finally {
    loading.value = false;
  }
}

let searchTimeout: any = null;
watch(search, () => { clearTimeout(searchTimeout); searchTimeout = setTimeout(() => { page.value = 1; fetchEmployees(); }, 400); });
watch(page, fetchEmployees);
onMounted(fetchEmployees);

async function handleDelete(id: number) {
  try {
    await api.del(`/employees/${id}/`);
    confirmDeleteId.value = null;
    fetchEmployees();
  } catch {
    errorMsg.value = "Failed to delete employee.";
  }
}

const totalPages = computed(() => Math.max(1, Math.ceil(count.value / 10)));
</script>

<template>
  <div>
    <div class="flex items-center justify-between mb-6">
      <h1 class="text-xl font-bold text-slate-800">Employees</h1>
      <NuxtLink to="/employees/new" class="bg-slate-900 hover:bg-slate-700 text-white text-sm font-medium px-4 py-2 rounded-lg transition">+ Add Employee</NuxtLink>
    </div>

    <input v-model="search" placeholder="Search by name, email or position..." class="w-full border rounded-lg px-3 py-2 mb-4" />
    <p v-if="errorMsg" class="text-red-600 text-sm mb-3">{{ errorMsg }}</p>
    <p v-if="loading" class="text-slate-500 text-sm">Loading...</p>

    <div v-if="!loading && employees.length" class="bg-white rounded-xl shadow overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-slate-100 text-left text-slate-600">
          <tr><th class="px-4 py-3">Name</th><th class="px-4 py-3">Department</th><th class="px-4 py-3">Position</th><th class="px-4 py-3">Status</th><th class="px-4 py-3 text-right">Actions</th></tr>
        </thead>
        <tbody>
          <tr v-for="emp in employees" :key="emp.id" class="border-t hover:bg-slate-50">
            <td class="px-4 py-3 font-medium">{{ emp.full_name }}</td>
            <td class="px-4 py-3">{{ emp.department_name || "—" }}</td>
            <td class="px-4 py-3">{{ emp.position }}</td>
            <td class="px-4 py-3"><span class="px-2 py-0.5 rounded-full text-xs bg-green-100 text-green-700 capitalize">{{ emp.status.replace('_',' ') }}</span></td>
            <td class="px-4 py-3 text-right space-x-2">
              <NuxtLink :to="`/employees/${emp.id}`" class="text-slate-900 hover:underline">Edit</NuxtLink>
              <button class="text-red-600 hover:underline" @click="confirmDeleteId = emp.id">Delete</button>
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

    <div v-if="confirmDeleteId" class="fixed inset-0 bg-black/40 flex items-center justify-center px-4 z-50">
      <div class="bg-white rounded-xl p-6 max-w-sm w-full">
        <p class="font-medium mb-4">Delete this employee? This cannot be undone.</p>
        <div class="flex justify-end gap-3">
          <button class="px-4 py-2 rounded border" @click="confirmDeleteId = null">Cancel</button>
          <button class="px-4 py-2 rounded bg-red-600 text-white" @click="handleDelete(confirmDeleteId)">Delete</button>
        </div>
      </div>
    </div>
  </div>
</template>
