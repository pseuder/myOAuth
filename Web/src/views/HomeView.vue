<!-- src/views/HomeView.vue -->
<template>
  <div>
    <div class="flex justify-center gap-4 p-4">
      <GoogleSendMail />
      <MicrosoftSendMail />
    </div>
  </div>
</template>

<script setup>
import GoogleSendMail from "@/components/GoogleSendMail.vue";
import MicrosoftSendMail from "@/components/MicrosoftSendMail.vue";
</script>

<style scoped></style>
