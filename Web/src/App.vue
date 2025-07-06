<template>
  <div>
    <header>
      <NavBar />
    </header>

    <main>
      {{ authStore.googleUserInfo }}
      {{ authStore.microsoftUserInfo }}
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useAuthStore } from "@/stores/auth";
import NavBar from "@/views/NavBar.vue";

const authStore = useAuthStore();

const userInfo = ref(null);

onMounted(() => {});
</script>

<style scoped></style>
