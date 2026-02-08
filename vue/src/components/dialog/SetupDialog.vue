<template>
  <v-dialog v-model="dialogState" width="400">
    <v-card>
      <v-form ref="nodeAddFormRef">
        <v-card-title>Setup</v-card-title>
        <v-card-text>
          初期設定を行います。管理者ユーザが存在する場合実行できません。
          <v-text-field
            v-model="postData.id"
            label="Admin user name"
            :rules="[required, limitLength64, characterRestrictions, firstCharacterRestrictions]"
            counter="64"
          />
          <v-text-field
            v-model="postData.password"
            :append-icon="show1 ? 'mdi-eye' : 'mdi-eye-off'"
            :rules="[required]"
            :type="show1 ? 'text' : 'password'"
            name="input-10-1"
            label="Password"
            hint="At least 1 characters"
            counter
            @click:append="show1 = !show1"
          />
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <v-btn color="primary" @click="runMethod">
            Setup
          </v-btn>
        </v-card-actions>
      </v-form>
    </v-card>
  </v-dialog>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { apiClient } from '@/func/client'
import { usePushNotice } from '@/composables/utility'
import { required, limitLength64, characterRestrictions, firstCharacterRestrictions } from '@/composables/rules'

const { pushNotice } = usePushNotice()

const nodeAddFormRef = ref()
const dialogState = ref(false)
const show1 = ref(false)

const postData = reactive({
  id: '',
  password: ''
})

const openDialog = () => {
  dialogState.value = true
}

const runMethod = async () => {
  const { valid } = await nodeAddFormRef.value.validate()
  if (!valid) {
    return
  }

  try {
    const { error } = await apiClient.POST('/api/auth/setup', {
      body: postData
    })
    if (error) throw error
    pushNotice('Success setup', 'success')
    dialogState.value = false
  } catch (error: unknown) {
    const fetchError = error as { detail?: string }
    pushNotice(fetchError.detail || 'セットアップに失敗しました', 'error')
  }
}

defineExpose({
  openDialog
})
</script>
