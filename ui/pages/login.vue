<template>
  <div class="Login">
    <v-container class="fill-height" fluid>
      <v-row justify="center">
        <v-col cols="12" sm="8" md="4">
          <!-- <v-card flat>
            <v-card-text class="text-center">
              <div class="body-1 mb-3">Now loading...</div>
              <v-progress-circular indeterminate color="primary" />
            </v-card-text>
          </v-card> -->
          <v-card >
            <v-toolbar color="primary">
              <v-toolbar-title>Login</v-toolbar-title>
              <v-spacer></v-spacer>
            </v-toolbar>
            <v-form ref="form">
              <v-card-text>
                <v-text-field
                  label="UserID"
                  name="userId"
                  prepend-icon="mdi-account"
                  required
                  variant="underlined"
                  type="text"
                  v-model="userId"
                ></v-text-field>

                <v-text-field
                  id="password"
                  label="Password"
                  name="password"
                  prepend-icon="mdi-lock"
                  required
                  variant="underlined"
                  v-model="password"
                  type="password"
                ></v-text-field>
              </v-card-text>
              <v-card-actions>
                <v-spacer></v-spacer>
                <v-btn
                  variant="flat"
                  color="primary"
                  @click="login(userId, password)"
                >Login</v-btn>
              </v-card-actions>
            </v-form>
          </v-card>
        </v-col>
      </v-row>
    </v-container>
  </div>
</template>

<script setup lang="ts">

const userId = ref("")
const password = ref("")

const login = (userId:string, password:string) => {
  console.log("login")
  const newFormData = new FormData();

  //append your file or image
  newFormData.append("password", password);
  newFormData.append("username", userId);
  const { data, pending, error, refresh } = useBaseFetch("/api/auth",{
    method: 'POST',
    body: newFormData
  })
  console.log(data.json())
};

</script>