SystemJS.config({
  baseURL: "/static",
  paths: {
    "google-maps": "https://maps.googleapis.com/maps/api/js?libraries=places&sensor=false&language=ko",
    "npm:": "jspm_packages/npm/",
    "jspm_0_17/": "js/"
  }
});
