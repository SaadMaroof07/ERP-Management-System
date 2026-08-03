<script setup lang="ts">
definePageMeta({ middleware: "auth" });

const api = useApi();
const logs = ref<any[]>([]);
const loading = ref(true);
const search = ref("");

async function fetchLogs() {
  loading.value = true;
  const data: any = await api.get("/auth/activity-logs/", { search: search.value || undefined });
  logs.value = data.results || data;
  loading.value = false;
}

let searchTimeout: any = null;
watch(search, () => { clearTimeout(searchTimeout); searchTimeout = setTimeout(fetchLogs, 400); });
onMounted(fetchLogs);

const actionColor: Record<string, string> = {
  create: "bg-green-100 text-green-700",
  update: "bg-blue-100 text-blue-700",
  delete: "bg-red-100 text-red-700",
  login: "bg-slate-200 text-slate-700",
};
</script>

<template>
  <div>
    <h1 class="text-xl font-bold text-slate-800 mb-6">Activity Logs</h1>
    <input v-model="search" placeholder="Search by module, action, user..." class="w-full border rounded-lg px-3 py-2 mb-4" />

    <p v-if="loading" class="text-slate-500 text-sm">Loading...</p>

    <div v-if="!loading" class="bg-white rounded-xl shadow overflow-x-auto">
      <table class="w-full text-sm">
        <thead class="bg-slate-100 text-left text-slate-600">
          <tr><th class="px-4 py-3">Time</th><th class="px-4 py-3">User</th><th class="px-4 py-3">Action</th><th class="px-4 py-3">Module</th><th class="px-4 py-3">Details</th></tr>
        </thead>
        <tbody>
          <tr v-for="log in logs" :key="log.id" class="border-t">
            <td class="px-4 py-3 text-slate-500 whitespace-nowrap">{{ new Date(log.created_at).toLocaleString() }}</td>
            <td class="px-4 py-3">{{ log.username || "system" }}</td>
            <td class="px-4 py-3"><span class="px-2 py-0.5 rounded-full text-xs capitalize" :class="actionColor[log.action]">{{ log.action }}</span></td>
            <td class="px-4 py-3 capitalize">{{ log.module }}</td>
            <td class="px-4 py-3 text-slate-600">{{ log.object_repr }} <span v-if="log.description" class="text-slate-400">— {{ log.description }}</span></td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>
