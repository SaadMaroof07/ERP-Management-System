export default defineNuxtConfig({
  compatibilityDate: "2024-07-01",
  devtools: { enabled: true },
  modules: ["@nuxtjs/tailwindcss", "@pinia/nuxt"],
  css: ["~/assets/css/main.css"],
  runtimeConfig: {
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || "http://127.0.0.1:8000/api",
    },
  },
  app: {
    head: {
      title: "Aptura ERP",
      meta: [{ name: "viewport", content: "width=device-width, initial-scale=1" }],
    },
  },
});
