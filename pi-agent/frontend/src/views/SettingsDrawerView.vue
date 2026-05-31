<template>
  <div class="settings-drawer-page">
    <van-popup
      v-model:show="showDrawer"
      position="right"
      :style="{ width: '86%', height: '100%' }"
      closeable
      @closed="handleClosed"
    >
      <div class="drawer-body">
        <van-nav-bar title="高级设置" left-arrow @click-left="closeDrawer" />

        <div class="drawer-content">
          <h3 class="drawer-title">路由配置</h3>
          <p class="drawer-desc">恢复后将重置为当前已保存的默认配置。</p>

          <van-button block type="danger" plain @click="handleResetConfig">
            恢复默认路由配置
          </van-button>
        </div>
      </div>
    </van-popup>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { showToast } from 'vant'
import { useRouter } from 'vue-router'
import { useNavigationStore } from '@/stores/navigation'

const router = useRouter()
const navStore = useNavigationStore()
const showDrawer = ref(false)

function closeDrawer() {
  showDrawer.value = false
}

function handleClosed() {
  router.replace({ name: 'settings' })
}

function handleResetConfig() {
  navStore.resetConfig()
  showToast('已恢复默认路由配置')
  closeDrawer()
}

onMounted(() => {
  showDrawer.value = true
})
</script>

<style scoped>
.settings-drawer-page {
  min-height: 100vh;
  background: transparent;
}

.drawer-body {
  height: 100%;
  background: #fff;
}

.drawer-content {
  padding: 16px;
}

.drawer-title {
  font-size: 16px;
  color: #323233;
  margin: 0 0 8px;
}

.drawer-desc {
  font-size: 13px;
  color: #969799;
  margin: 0 0 16px;
  line-height: 1.5;
}
</style>
