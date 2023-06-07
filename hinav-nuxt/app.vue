<template>
  <v-app>
    <v-app-bar
      color="primary"
      density="compact"
    >
      <v-app-bar-nav-icon
      ></v-app-bar-nav-icon>
      <v-toolbar-title></v-toolbar-title>
      <v-spacer></v-spacer>
      <v-text-field
        density="compact"
        variant="outlined"
        append-inner-icon="mdi-magnify"
        single-line
        hide-details
      ></v-text-field>
      <v-btn icon><v-icon>mdi-reload</v-icon></v-btn>
    </v-app-bar>
  </v-app>
</template>

<script>
const url = "";

const headers = new Headers({
  Authorization: `...`,
});
const res = await fetch(url, {
  method: "GET",
  headers: headers,
});
const resData = await res.json();
console.log(`** ${res.status}`, resData);
</script>