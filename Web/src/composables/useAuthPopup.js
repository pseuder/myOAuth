import { ref, onMounted, onUnmounted } from "vue";
import { useAuthStore } from "@/stores/auth";

export function useAuthPopup(provider, onLoginSuccess, onLogout) {
  const authStore = useAuthStore();
  const loading = ref(false);
  let authWindow = null;

  const handleLogin = async () => {
    loading.value = true;
    const url = await authStore.login(provider);
    if (url) {
      const width = 600,
        height = 700;
      const left = window.screen.width / 2 - width / 2;
      const top = window.screen.height / 2 - height / 2;
      authWindow = window.open(
        url,
        "Auth",
        `width=${width},height=${height},top=${top},left=${left}`,
      );
    } else {
      console.error("Could not get authorization URL");
      loading.value = false;
    }
    console.log("Opening auth window for provider:", provider);
    // Loading state is handled by the message handler
  };

  const handleLogout = () => {
    if (authWindow) {
      authWindow.close();
      authWindow = null;
    }
    authStore.logout();
    if (onLogout) {
      onLogout();
    }
  };

  const handleAuthMessage = (event) => {
    // Ensure the message is from the auth window we opened
    if (event.source !== authWindow) {
      return;
    }

    const {
      status,
      provider: eventProvider,
      userInfo,
      accessToken,
    } = event.data;

    // Ensure the message is for the correct provider instance
    if (eventProvider !== provider) {
      return;
    }

    if (status === "success" && userInfo && accessToken) {
      // Call the new action in the auth store
      authStore.handleLoginCallback({ provider, userInfo, accessToken });

      // Call the success callback if it exists
      if (onLoginSuccess) {
        onLoginSuccess(userInfo);
      }
    } else {
      console.error("Authentication failed or data is missing.", event.data);
    }

    if (authWindow) {
      authWindow.close();
      authWindow = null;
    }
    loading.value = false;
  };

  onMounted(() => {
    window.addEventListener("message", handleAuthMessage);
  });

  onUnmounted(() => {
    window.removeEventListener("message", handleAuthMessage);
  });

  return {
    loading,
    handleLogin,
    handleLogout,
  };
}
