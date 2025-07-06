<template>
  <div class="flex h-16 items-center justify-center bg-gray-100">
    <router-link to="/">
      <div
        class="flex h-full items-center px-4 text-gray-700 hover:text-gray-900"
      >
        <el-icon><HomeFilled /></el-icon>
        <span class="ml-2">首頁</span>
      </div>
    </router-link>

    <div class="ml-auto flex h-full items-center">
      <GoogleLogin />
      <MicrosoftLogin />
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";

import GoogleLogin from "@/components/GoogleLogin.vue";
import MicrosoftLogin from "@/components/MicrosoftLogin.vue";

onMounted(() => {});
</script>
