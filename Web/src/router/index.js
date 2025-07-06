import { createRouter, createWebHistory } from "vue-router";
import HomeView from "../views/HomeView.vue";
import { useAuthStore } from "@/stores/auth";

// 定義路由
const routes = [
  {
    path: "/",
    name: "home",
    component: HomeView,
  },
];

// 建立 router 實例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

// Navigation Guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();
  const requiresAuth = to.matched.some((record) => record.meta.requiresAuth);

  // Check for session on initial load
  if (!authStore.isLoggedIn && localStorage.getItem("isLoggedIn")) {
    authStore.fetchUser();
  }

  if (requiresAuth && !authStore.isAuthenticated) {
    // If the user is not authenticated, redirect to the home page.
    // You could also redirect to a dedicated login page.
    next({ name: "home" });
  } else {
    next(); // Proceed to the route
  }
});

// 導出 router
export default router;
