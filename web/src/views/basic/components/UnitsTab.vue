<template>
  <div class="units-tab">
    <div class="tab-toolbar">
      <div class="toolbar-left">
        <el-input
          v-model="localSearch"
          placeholder="搜索计量单位"
          style="width: 200px"
          clearable
          @input="$emit('search', localSearch)"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
      </div>
      <div class="toolbar-right">
        <el-button type="primary" :icon="Plus" @click="$emit('add')">新增单位</el-button>
      </div>
    </div>
    
    <el-table
      :data="filteredUnitList"
      v-loading="unitLoading"
      border
      stripe
      highlight-current-row
      @row-click="(row) => $emit('click', row)"
    >
      <el-table-column prop="name" label="单位名称" min-width="150" />
      <el-table-column label="状态" width="100" align="center">
        <template #default="{ row }">
          <el-switch
            :model-value="row.is_active"
            :before-change="() => handleBeforeChange(row)"
            :loading="unitToggleLoading === row.id"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="150" align="center">
        <template #default="{ row }">
          <el-button type="primary" link size="small" @click.stop="$emit('edit', row)">编辑</el-button>
          <el-button type="danger" link size="small" @click.stop="$emit('delete', row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>
    
    <el-dialog
      :model-value="unitDialogVisible"
      :title="unitDialogTitle"
      width="400px"
      destroy-on-close
      @close="$emit('dialog-close')"
    >
      <el-form
        ref="formRef"
        :model="unitForm"
        :rules="unitRules"
        label-width="80px"
      >
        <el-form-item label="单位名称" prop="name">
          <el-input v-model="unitForm.name" placeholder="请输入单位名称" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="$emit('dialog-close')">取消</el-button>
        <el-button type="primary" @click="$emit('submit')" :loading="unitSubmitLoading">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue'
import { ElMessageBox } from 'element-plus'
import { Plus, Search } from '@element-plus/icons-vue'

const props = defineProps({
  unitList: { type: Array, default: () => [] },
  unitLoading: { type: Boolean, default: false },
  unitSearch: { type: String, default: '' },
  selectedUnit: { type: Object, default: null },
  unitDialogVisible: { type: Boolean, default: false },
  unitDialogTitle: { type: String, default: '' },
  unitForm: { type: Object, default: () => ({}) },
  unitRules: { type: Object, default: () => ({}) },
  unitSubmitLoading: { type: Boolean, default: false },
  unitToggleLoading: { type: [Number, null], default: null },
  filteredUnitList: { type: Array, default: () => [] }
})

const emit = defineEmits(['search', 'add', 'edit', 'delete', 'toggle-status', 'click', 'submit', 'dialog-close'])

const localSearch = ref(props.unitSearch)
const formRef = ref(null)

watch(() => props.unitSearch, (val) => {
  localSearch.value = val
})

const handleBeforeChange = async (row) => {
  const newStatus = !row.is_active
  try {
    await ElMessageBox.confirm(
      `确定要${newStatus ? '启用' : '停用'}单位「${row.name}」吗？`,
      '提示',
      { type: 'warning' }
    )
    row.is_active = newStatus
    emit('toggle-status', row)
    return true
  } catch {
    return false
  }
}

defineExpose({ formRef })
</script>

<style scoped>
.units-tab {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.tab-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
</style>
