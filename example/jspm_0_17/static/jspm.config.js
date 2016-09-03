SystemJS.config({
  nodeConfig: {
    "paths": {
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
    }
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
