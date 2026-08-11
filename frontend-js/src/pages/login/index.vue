<!--
  文件路径: /frontend-js/src/pages/login/index.vue
  功能描述: 登录内容页
  主要功能:
    - 用户登录认证
    - 演示账号填充
    - 未登录布局内内容渲染
-->
<template>
  <div class="login-container">
    <div class="login-shell">
      <section class="login-hero">
        <div class="hero-brand-surface">
          <BrandLogo class="hero-brand-logo" variant="hero" />
        </div>

        <div class="hero-copy">
          <h1 class="brand-title">{{ $t('common.systemTitle') }}</h1>
          <p class="brand-subtitle">{{ $t('login.subtitle') }}</p>
        </div>

        <div class="hero-ornament">
          <div class="ornament-card">
            <div class="ornament-line strong"></div>
            <div class="ornament-line"></div>
            <div class="ornament-line short"></div>
          </div>
          <div class="ornament-grid">
            <span></span>
            <span></span>
            <span></span>
            <span></span>
          </div>
        </div>
      </section>

      <section class="login-card">
        <div class="login-brand">
          <div class="brand-icon">
            <el-icon :size="22"><Platform /></el-icon>
          </div>
          <div class="brand-meta">
            <span class="login-heading">{{ $t('login.login') }}</span>
            <span class="login-caption">{{ $t('login.subtitle') }}</span>
          </div>
        </div>

        <el-form
          ref="loginFormRef"
          :model="loginForm"
          :rules="loginRules"
          class="login-form"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              :placeholder="$t('login.username')"
              size="large"
              prefix-icon="User"
              clearable
              class="login-input"
            />
          </el-form-item>

          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              :placeholder="$t('login.password')"
              size="large"
              prefix-icon="Lock"
              show-password
              class="login-input"
              @keyup.enter="handleLogin"
            />
          </el-form-item>

          <div class="form-row">
            <el-checkbox v-model="rememberMe" class="remember-checkbox">
              {{ $t('login.rememberMe') }}
            </el-checkbox>
          </div>

          <el-form-item>
            <el-button
              type="primary"
              size="large"
              :loading="loading"
              class="login-btn"
              @click="handleLogin"
            >
              {{ loading ? $t('login.loggingIn') : $t('login.login') }}
            </el-button>
          </el-form-item>
        </el-form>

        <div v-if="isLoginDemoAccountsEnabled" class="demo-card">
          <div class="demo-card-header">
            <el-icon><InfoFilled /></el-icon>
            <span>{{ $t('login.demoAccount') }}</span>
          </div>
          <div class="demo-card-body">
            <div
              v-for="account in demoAccounts"
              :key="account.role"
              class="demo-account-item"
              @click="fillAccount(account)"
            >
              <span class="demo-role">{{ $t(`login.roles.${account.role}`) }}</span>
              <span class="demo-username">{{ account.username }}</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useUserStore } from '@/store/user'
import { ElMessage } from 'element-plus'
import { useI18n } from 'vue-i18n'
import { InfoFilled } from '@element-plus/icons-vue'
import { isLoginDemoAccountsEnabled } from '@/config/permissions'
import BrandLogo from '@/components/shell/BrandLogo.vue'

const router = useRouter()
const userStore = useUserStore()
const { t } = useI18n()

const loginFormRef = ref()
const loading = ref(false)
const rememberMe = ref(false)

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [
    { required: true, message: t('login.rules.usernameRequired'), trigger: 'blur' },
    { min: 3, max: 20, message: t('login.rules.usernameLength'), trigger: 'blur' }
  ],
  password: [
    { required: true, message: t('login.rules.passwordRequired'), trigger: 'blur' },
    { min: 6, max: 20, message: t('login.rules.passwordLength'), trigger: 'blur' }
  ]
}

const demoAccounts = [
  { role: 'supervisor', username: 'supervisor', password: 'supervisor123', type: '' },
  { role: 'operator', username: 'operator', password: 'operator123', type: 'success' },
]

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        await userStore.login(loginForm)

        if (rememberMe.value) {
          localStorage.setItem('rememberedUsername', loginForm.username)
        } else {
          localStorage.removeItem('rememberedUsername')
        }

        ElMessage.success(t('common.success'))

        setTimeout(() => {
          router.replace('/')
        }, 300)
      } catch (error) {
        console.error('登录错误:', error)
        const status = error.response?.status ?? error.code
        const messageKey = Number(status) === 401
          ? 'login.messages.invalidCredentials'
          : 'login.messages.failed'
        ElMessage.error(t(messageKey))
      } finally {
        loading.value = false
      }
    }
  })
}

const fillAccount = (account) => {
  loginForm.username = account.username
  loginForm.password = account.password
}

const rememberedUsername = localStorage.getItem('rememberedUsername')
if (rememberedUsername) {
  loginForm.username = rememberedUsername
  rememberMe.value = true
}
</script>

<style scoped>
.login-container {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 1120px;
}

.login-shell {
  display: grid;
  grid-template-columns: 1.08fr 0.92fr;
  overflow: hidden;
  border: 1px solid var(--border-primary);
  border-radius: 32px;
  background: var(--bg-panel);
  box-shadow: var(--shadow-xl);
  backdrop-filter: blur(30px);
  -webkit-backdrop-filter: blur(30px);
}

.login-hero,
.login-card {
  position: relative;
  padding: 40px;
}

.login-hero {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  min-height: 620px;
  background:
    linear-gradient(180deg, rgba(255, 255, 255, 0.02), transparent),
    radial-gradient(circle at 18% 18%, rgba(113, 112, 255, 0.18), transparent 28%),
    transparent;
  border-right: 1px solid var(--border-secondary);
}

.hero-brand-surface {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  width: 224px;
  height: 80px;
}

.hero-brand-logo {
  width: 100%;
  height: 100%;
}

.hero-copy {
  max-width: 460px;
}

.brand-title {
  margin: 0 0 16px;
  font-size: clamp(40px, 6vw, 64px);
  line-height: 0.96;
  letter-spacing: -0.05em;
  font-weight: 590;
  color: var(--text-primary);
}

.brand-subtitle {
  margin: 0;
  max-width: 360px;
  font-size: 16px;
  line-height: 1.7;
  color: var(--text-secondary);
}

.hero-ornament {
  display: grid;
  grid-template-columns: minmax(0, 1.3fr) 120px;
  gap: 16px;
  align-items: end;
}

.ornament-card {
  padding: 20px;
  border: 1px solid var(--border-primary);
  border-radius: 24px;
  background: rgba(255, 255, 255, 0.03);
}

.ornament-line {
  height: 12px;
  margin-bottom: 12px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.06);
}

.ornament-line.strong {
  width: 72%;
  background: linear-gradient(90deg, var(--primary), rgba(255, 255, 255, 0.08));
}

.ornament-line.short {
  width: 46%;
  margin-bottom: 0;
}

.ornament-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.ornament-grid span {
  aspect-ratio: 1;
  border: 1px solid var(--border-primary);
  border-radius: 18px;
  background: linear-gradient(180deg, rgba(255, 255, 255, 0.04), transparent);
}

.login-card {
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.login-brand {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-bottom: 28px;
}

.brand-icon {
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--primary), var(--primary-light));
  color: var(--text-inverse);
  box-shadow: 0 18px 36px rgba(94, 106, 210, 0.28);
}

.brand-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.login-heading {
  font-size: 20px;
  font-weight: 590;
  letter-spacing: -0.03em;
  color: var(--text-primary);
}

.login-caption {
  font-size: 13px;
  color: var(--text-tertiary);
}

.login-form {
  text-align: left;
  margin-bottom: 24px;
}

.login-form :deep(.el-form-item) {
  margin-bottom: 18px;
}

.login-input {
  --el-input-height: 48px;
}

.form-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 18px;
}

.remember-checkbox {
  color: var(--text-secondary);
}

.login-btn {
  width: 100%;
  height: 48px;
  font-size: 15px;
  font-weight: 590;
  border-radius: 14px;
  box-shadow: 0 22px 44px rgba(94, 106, 210, 0.24);
}

.demo-card {
  padding: 20px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.03);
  border: 1px solid var(--border-primary);
}

.demo-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 14px;
  color: var(--text-secondary);
  font-weight: 510;
}

.demo-card-body {
  display: grid;
  gap: 10px;
}

.demo-account-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  border-radius: 14px;
  cursor: pointer;
  background: rgba(255, 255, 255, 0.02);
  border: 1px solid var(--border-secondary);
}

.demo-account-item:hover {
  border-color: var(--border-primary);
  background: rgba(255, 255, 255, 0.05);
}

.demo-role {
  font-weight: 510;
  color: var(--text-primary);
}

.demo-username {
  font-family: var(--font-mono);
  color: var(--text-tertiary);
  font-size: 13px;
}

@media (max-width: 980px) {
  .login-shell {
    grid-template-columns: 1fr;
  }

  .login-hero {
    min-height: auto;
    gap: 40px;
    border-right: none;
    border-bottom: 1px solid var(--border-secondary);
  }
}

@media (max-width: 768px) {
  .login-hero,
  .login-card {
    padding: 24px 20px;
  }

  .hero-brand-surface {
    width: 192px;
    height: 68px;
  }

  .hero-ornament {
    grid-template-columns: 1fr;
  }

  .brand-title {
    font-size: 38px;
  }
}
</style>
