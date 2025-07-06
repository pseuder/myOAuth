<template>
  <div>
    <h3>Send Google Mail</h3>
    <el-card>
      <el-form
        ref="formRef"
        :model="formModel"
        :rules="rules"
        label-width="auto"
      >
        <el-form-item label="To:" prop="recipient">
          <el-input
            v-model="formModel.recipient"
            placeholder="請輸入收件人信箱"
          />
        </el-form-item>

        <el-form-item label="Subject:" prop="subject">
          <el-input v-model="formModel.subject" placeholder="請輸入主旨" />
        </el-form-item>

        <el-form-item label="Body:" prop="body">
          <el-input
            v-model="formModel.body"
            type="textarea"
            :rows="4"
            placeholder="請輸入信件內容"
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="submitForm()">Send</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from "vue";
import { ElMessage } from "element-plus";
import { useAPI } from "@/composables/useAPI";

const { sendGoogleEmail } = useAPI();

const formRef = ref(null);
const formModel = reactive({
  recipient: "",
  subject: "",
  body: "",
});

const rules = reactive({
  recipient: [
    { required: true, message: "請輸入收件人信箱", trigger: "blur" },
    {
      type: "email",
      message: "請輸入有效的信箱格式",
      trigger: ["blur", "change"],
    },
  ],
  subject: [{ required: true, message: "請輸入主旨", trigger: "blur" }],
  body: [{ required: true, message: "請輸入信件內容", trigger: "blur" }],
});

const submitForm = async () => {
  let res = await sendGoogleEmail(formModel);
  if (res && res.status === "success") {
    ElMessage.success(
      "信件已成功使用 Google 發送至收件人 " + formModel.recipient,
    );
    formRef.value.resetFields();
  } else {
    console.error("發送失敗", res);
    ElMessage.error("發送失敗，請稍後再試");
  }
};
</script>

<style scoped>
.el-card {
  max-width: 500px;
  margin: auto;
}
</style>
