SystemJS.config({
  nodeConfig: {
    "paths": {
      "google-maps": "https://maps.googleapis.com/maps/api/js?libraries=places&sensor=false&language=ko",
      "jspm_0_17/": "js/"
    }
  },
  devConfig: {
    "map": {
      "plugin-babel": "npm:systemjs-plugin-babel@0.0.13"
    }
  },
  transpiler: "plugin-babel",
  packages: {
    "jspm_0_17": {
      "format": "esm",
      "main": "main.js",
      "meta": {
        "*.js": {
          "loader": "plugin-babel"
        }
      }
    },
    "https://maps.googleapis.com": {
      "defaultExtension": false,
      "meta": {
        "*": {
          "scriptLoad": true,
          "exports": "google"
        }
      }
    },
  }
});

SystemJS.config({
  packageConfigPaths: [
    "npm:@*/*.json",
    "npm:*.json"
  ],
  map: {},
  packages: {}
});
