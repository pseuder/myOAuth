<template>
  <div class="flex flex-col h-[85vh] gap-2">
    <div class="h-[5%] overflow-none">
      <el-button type="primary" @click="handleAdd">新增用戶</el-button>
    </div>
    <div class="h-[80%] w-full overflow-auto">
      <el-table
        v-loading="loading"
        :data="paginatedData"
        style="width: 100%"
        height="100%"
      >
        <el-table-column
          v-for="(value, key) in columnKeys"
          :key="key"
          :prop="key"
          :label="value"
          show-overflow-tooltip
        >
        </el-table-column>

        <el-table-column label="操作" width="150">
          <template #default="{ row }">
            <div class="flex">
              <el-button type="primary" size="small" @click="handleEdit(row)"
                >編輯</el-button
              >
              <el-button type="danger" size="small" @click="handleDelete(row)"
                >刪除</el-button
              >
            </div>
          </template>
        </el-table-column>
      </el-table>
    </div>
    <div class="h-[5%] overflow-none">
      <el-pagination
        v-model:current-page="currentPage"
        v-model:page-size="pageSize"
        :page-sizes="[10, 20, 30, 50, 100]"
        :total="total"
        @size-change="handleSizeChange"
        @current-change="handleCurrentChange"
        layout="total, sizes, prev, pager, next, jumper"
      />
    </div>
  </div>

  <!-- 新增/編輯/刪除用戶的彈窗 -->
  <el-dialog v-model="dialogVisible" :title="dialogTitle" width="50%">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="formRules"
      label-width="100px"
    >
      <el-form-item label="用戶名" prop="username">
        <el-input v-model="formData.username" />
      </el-form-item>
      <el-form-item label="郵箱" prop="email">
        <el-input v-model="formData.email" />
      </el-form-item>
      <el-form-item label="角色" prop="roles">
        <el-input v-model="formData.roles" />
      </el-form-item>
      <el-form-item label="備註" prop="note">
        <el-input v-model="formData.note" type="textarea" />
      </el-form-item>
      <el-form-item label="可見欄位" prop="visible_column">
        <el-input v-model="formData.visible_column" />
      </el-form-item>
      <el-form-item label="是否啟用" prop="is_active">
        <el-input v-model="formData.is_active" />
      </el-form-item>
    </el-form>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit">確定</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, computed, onMounted } from "vue";
import { ElMessage, ElMessageBox } from "element-plus";

import * as API_service from "@/API_service.js";

// 響應式狀態
const loading = ref(false);
const tableData = ref([]); // 存儲所有數據
const currentPage = ref(1);
const pageSize = ref(10);

const columnKeys = ref({
  id: "ID",
  username: "用戶名",
  email: "郵箱",
  roles: "角色",
  note: "備註",
  visible_column: "可見欄位",
  is_active: "是否啟用",
  created_time: "創建時間",
  updated_time: "更新時間",
});

const dialogVisible = ref(false);
const dialogTitle = ref("");
const dialogType = ref(""); // 'add' | 'edit' | 'delete'
const formRef = ref(null);
const formData = ref({
  username: "",
  email: "",
  roles: "",
  note: "",
  visible_column: "",
  is_active: 1,
});

// 表單驗證規則
const formRules = {
  username: [{ required: true, message: "請輸入用戶名", trigger: "blur" }],
  email: [
    { required: true, message: "請輸入郵箱", trigger: "blur" },
    { type: "email", message: "請輸入正確的郵箱格式", trigger: "blur" },
  ],
  roles: [{ required: true, message: "請輸入角色", trigger: "blur" }],
};

//-- 動態計算 --//

// 計算總數據量
const total = computed(() => tableData.value.length);

// 計算當前頁的數據
const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value;
  const end = start + pageSize.value;
  return tableData.value.slice(start, end);
});

// 獲取所有數據
const fetchData = async () => {
  try {
    loading.value = true;
    const res = await API_service.GET_API("get_all_user");

    if (res.status === "success") {
      tableData.value = res.data;
    } else {
      ElMessage.error(res.message || "獲取數據失敗");
    }
  } catch (error) {
    console.error("獲取數據失敗:", error);
    ElMessage.error("獲取數據失敗，請稍後再試");
  } finally {
    loading.value = false;
  }
};

// 處理分頁大小變化
const handleSizeChange = (val) => {
  pageSize.value = val;
  currentPage.value = 1; // 重置到第一頁
};

// 處理頁碼變化
const handleCurrentChange = (val) => {
  currentPage.value = val;
};

// 組件掛載時獲取數據
onMounted(() => {
  fetchData();
});

// 新增用戶
const handleAdd = () => {
  dialogType.value = "add";
  dialogTitle.value = "新增用戶";
  formData.value = {
    username: "",
    email: "",
    roles: "",
    note: "",
    visible_column: "",
    is_active: 1,
  };
  dialogVisible.value = true;
};

// 編輯用戶
const handleEdit = (row) => {
  dialogType.value = "edit";
  dialogTitle.value = "編輯用戶";
  formData.value = { ...row };
  dialogVisible.value = true;
};

// 刪除用戶
const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm("確認要刪除該用戶嗎？", "提示", {
      confirmButtonText: "確定",
      cancelButtonText: "取消",
      type: "warning",
    });

    loading.value = true;
    const res = await API_service.DELETE_API(`delete_user/${row.id}`);

    if (res.status === "success") {
      ElMessage.success("刪除成功");
      await fetchData(); // 重新獲取數據
    } else {
      ElMessage.error(res.message || "刪除失敗");
    }
  } catch (error) {
    if (error !== "cancel") {
      console.error("刪除失敗:", error);
      ElMessage.error("刪除失敗，請稍後再試");
    }
  } finally {
    loading.value = false;
  }
};

const handleSubmit = async () => {
  if (!formRef.value) return;

  try {
    await formRef.value.validate();
    loading.value = true;

    let res;
    if (dialogType.value === "add") {
      res = await API_service.POST_API("add_user", formData.value);
    } else if (dialogType.value === "edit") {
      res = await API_service.PUT_API(
        `update_user/${formData.value.id}`,
        formData.value
      );
    }

    if (res.status === "success") {
      ElMessage.success(dialogType.value === "add" ? "新增成功" : "更新成功");
      dialogVisible.value = false;
      await fetchData(); // 重新獲取數據
    } else {
      ElMessage.error(
        res.message || (dialogType.value === "add" ? "新增失敗" : "更新失敗")
      );
    }
  } catch (error) {
    console.error("操作失敗:", error);
    ElMessage.error("操作失敗，請稍後再試");
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
:deep(.el-pagination) {
  justify-content: center;
}
</style>