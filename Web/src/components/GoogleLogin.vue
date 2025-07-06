<template>
  <div class="h-full w-full rounded-lg" :body-class="'p-0 h-full w-full'">
    <div class="flex h-full w-full items-center justify-center p-2 text-center">
      <!-- 登入按鈕 -->
      <template v-if="!userInfo">
        <el-button type="primary" @click="handleLogin" :loading="loading">
          Login with Google
        </el-button>
      </template>
      <template v-else>
        <img
          v-if="userInfo.picture"
          :src="userInfo.picture"
          alt="User Avatar"
          class="h-full w-auto rounded-full object-cover ring-4 ring-indigo-300"
        />
        <div v-if="userInfo" class="flex w-fit flex-col items-center">
          {{ userInfo?.name }}
          <el-button
            type="danger"
            class="ml-2"
            @click="handleLogout"
            size="small"
          >
            Logout</el-button
          >
        </div>
      </template>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from "vue";
import { useAuthPopup } from "@/composables/useAuthPopup";
import { useAuthStore } from "@/stores/auth";

const authStore = useAuthStore();
const userInfo = ref(null);

const googleLogin = (receivedUserInfo) => {
  userInfo.value = receivedUserInfo;
  authStore.handleLoginCallback("google", receivedUserInfo);
};

const googleLogout = () => {
  userInfo.value = null;
};

const { loading, handleLogin, handleLogout } = useAuthPopup(
  "google",
  googleLogin,
  googleLogout,
);

onMounted(() => {
  let authStoreUserInfo = authStore.googleUserInfo;
  console.log("Google user info:", authStoreUserInfo);
  if (authStoreUserInfo) {
    userInfo.value = {
      name: authStoreUserInfo.name,
      email: authStoreUserInfo.email,
      picture: authStoreUserInfo.picture,
    };
  }
});
</script>
