# Example django-systemjs project - JSPM 0.17.x (beta)

This is an example project with the default Django project layout.

It uses the JSPM 0.17, which is currently in beta.

In `frontend.sh` you see the tasks that would typically be executed during
deployment.


## Setup

This is a history of the commands used to come to this basic set-up.

### Bootstrap the `package.json`

```sh
$ npm init
```

`nspm init` starts an interactive shell prompt. The defaults should be fine,
but I made some changes to show that it's possible.


```plain
This utility will walk you through creating a package.json file.
It only covers the most common items, and tries to guess sensible defaults.

See `npm help json` for definitive documentation on these fields
and exactly what they do.

Use `npm install <pkg> --save` afterwards to install a package and
save it as a dependency in the package.json file.

Press ^C at any time to quit.
name: (jspm_0_17) <enter>
version: (1.0.0) <enter>
description: Example django+jspm 0.17 project
entry point: (index.js) main.js
test command: <enter>
git repository: https://github.com/sergei-maertens/django-systemjs.git
keywords: django,jspm,es6
author: Sergei Maertens <sergeimaertens@gmail.com>
license: (ISC) MIT
About to write to /home/bbt/coding/django-systemjs/example/jspm_0_17/package.json:

{
  "name": "jspm_0_17",
  "version": "1.0.0",
  "description": "Example django+jspm 0.17 project",
  "main": "main.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "repository": {
    "type": "git",
    "url": "git+https://github.com/sergei-maertens/django-systemjs.git"
  },
  "keywords": [
    "django",
    "jspm",
    "es6"
  ],
  "author": "Sergei Maertens <sergeimaertens@gmail.com>",
  "license": "MIT",
  "bugs": {
    "url": "https://github.com/sergei-maertens/django-systemjs/issues"
  },
  "homepage": "https://github.com/sergei-maertens/django-systemjs#readme"
}


Is this ok? (yes) <enter>
```

The basic `package.json` is ready now. We will only use `npm` for development
tooling, not for project dependencies.


### Adding `jspm` as dev-dependency.

```sh
$ npm install jspm@beta --save-dev
```

Expected output (version numbers can differ):
```
jspm_0_17@1.0.0 /home/bbt/coding/django-systemjs/example/jspm_0_17
└─┬ jspm@0.17.0-beta.14
  ├── bluebird@3.3.5
  ├─┬ chalk@1.1.3
  │ ├── ansi-styles@2.2.1
  │ ├── escape-string-regexp@1.0.5
  │ ├─┬ has-ansi@2.0.0
  │ │ └── ansi-regex@2.0.0
  │ ├── strip-ansi@3.0.1
  │ └── supports-color@2.0.0
  ├── core-js@1.2.6
  ├─┬ glob@6.0.4
  │ ├─┬ inflight@1.0.4
  │ │ └── wrappy@1.0.1
  │ ├── inherits@2.0.1
  │ ├── once@1.3.3
  │ └── path-is-absolute@1.0.0
  ├── graceful-fs@4.1.3
  ├─┬ jspm-github@0.14.6
  │ ├─┬ expand-tilde@1.2.1
  │ │ └── os-homedir@1.0.1
  │ ├── netrc@0.1.4
  │ ├─┬ request@2.53.0
  │ │ ├── aws-sign2@0.5.0
  │ │ ├─┬ bl@0.9.5
  │ │ │ └─┬ readable-stream@1.0.34
  │ │ │   └── isarray@0.0.1
  │ │ ├── caseless@0.9.0
  │ │ ├─┬ combined-stream@0.0.7
  │ │ │ └── delayed-stream@0.0.5
  │ │ ├── forever-agent@0.5.2
  │ │ ├─┬ form-data@0.2.0
  │ │ │ └── async@0.9.2
  │ │ ├── hawk@2.3.1
  │ │ ├─┬ http-signature@0.10.1
  │ │ │ ├── asn1@0.1.11
  │ │ │ ├── assert-plus@0.1.5
  │ │ │ └── ctype@0.5.3
  │ │ ├─┬ mime-types@2.0.14
  │ │ │ └── mime-db@1.12.0
  │ │ ├── oauth-sign@0.6.0
  │ │ └── qs@2.3.3
  │ ├─┬ rimraf@2.3.4
  │ │ └─┬ glob@4.5.3
  │ │   └── minimatch@2.0.10
  │ ├─┬ tar@2.2.1
  │ │ ├── block-stream@0.0.9
  │ │ └── fstream@1.0.8
  │ └─┬ which@1.2.4
  │   ├─┬ is-absolute@0.1.7
  │   │ └── is-relative@0.1.3
  │   └── isexe@1.1.2
  ├─┬ jspm-npm@0.28.10
  │ ├─┬ readdirp@2.0.0
  │ │ ├── minimatch@2.0.10
  │ │ └─┬ readable-stream@2.1.2
  │ │   ├── core-util-is@1.0.2
  │ │   ├── isarray@1.0.0
  │ │   ├── process-nextick-args@1.0.6
  │ │   ├── string_decoder@0.10.31
  │ │   └── util-deprecate@1.0.2
  │ ├─┬ request@2.58.0
  │ │ ├── caseless@0.10.0
  │ │ ├─┬ combined-stream@1.0.5
  │ │ │ └── delayed-stream@1.0.0
  │ │ ├── forever-agent@0.6.1
  │ │ ├─┬ form-data@1.0.0-rc4
  │ │ │ ├── async@1.5.2
  │ │ │ └─┬ mime-types@2.1.11
  │ │ │   └── mime-db@1.23.0
  │ │ ├─┬ har-validator@1.8.0
  │ │ │ └── bluebird@2.10.2
  │ │ ├── http-signature@0.11.0
  │ │ ├── oauth-sign@0.8.1
  │ │ └── qs@3.1.0
  │ ├─┬ rmdir@1.1.0
  │ │ └─┬ node.flow@1.2.3
  │ │   └─┬ node.extend@1.0.8
  │ │     ├── is@0.2.7
  │ │     └── object-keys@0.4.0
  │ └── tar@1.0.3
  ├─┬ jspm-registry@0.4.1
  │ ├── rsvp@3.2.1
  │ └── semver@4.3.6
  ├─┬ liftoff@2.2.1
  │ ├── extend@2.0.1
  │ ├─┬ findup-sync@0.3.0
  │ │ └── glob@5.0.15
  │ ├── flagged-respawn@0.3.2
  │ ├── rechoir@0.6.2
  │ └── resolve@1.1.7
  ├─┬ minimatch@3.0.0
  │ └─┬ brace-expansion@1.1.4
  │   ├── balanced-match@0.4.1
  │   └── concat-map@0.0.1
  ├─┬ mkdirp@0.5.1
  │ └── minimist@0.0.8
  ├── ncp@2.0.0
  ├─┬ proper-lockfile@1.1.2
  │ ├── err-code@1.1.1
  │ ├── extend@3.0.0
  │ └── retry@0.9.0
  ├─┬ request@2.72.0
  │ ├── aws-sign2@0.6.0
  │ ├─┬ aws4@1.3.2
  │ │ └─┬ lru-cache@4.0.1
  │ │   ├── pseudomap@1.0.2
  │ │   └── yallist@2.0.0
  │ ├─┬ bl@1.1.2
  │ │ └─┬ readable-stream@2.0.6
  │ │   └── isarray@1.0.0
  │ ├── caseless@0.11.0
  │ ├─┬ combined-stream@1.0.5
  │ │ └── delayed-stream@1.0.0
  │ ├── extend@3.0.0
  │ ├── forever-agent@0.6.1
  │ ├─┬ form-data@1.0.0-rc4
  │ │ └── async@1.5.2
  │ ├─┬ har-validator@2.0.6
  │ │ ├─┬ is-my-json-valid@2.13.1
  │ │ │ ├── generate-function@2.0.0
  │ │ │ ├─┬ generate-object-property@1.2.0
  │ │ │ │ └── is-property@1.0.2
  │ │ │ ├── jsonpointer@2.0.0
  │ │ │ └── xtend@4.0.1
  │ │ └─┬ pinkie-promise@2.0.1
  │ │   └── pinkie@2.0.4
  │ ├─┬ hawk@3.1.3
  │ │ ├── boom@2.10.1
  │ │ ├── cryptiles@2.0.5
  │ │ ├── hoek@2.16.3
  │ │ └── sntp@1.0.9
  │ ├─┬ http-signature@1.1.1
  │ │ ├── assert-plus@0.2.0
  │ │ ├─┬ jsprim@1.2.2
  │ │ │ ├── extsprintf@1.0.2
  │ │ │ ├── json-schema@0.2.2
  │ │ │ └── verror@1.3.6
  │ │ └─┬ sshpk@1.8.3
  │ │   ├── asn1@0.2.3
  │ │   ├── assert-plus@1.0.0
  │ │   ├─┬ dashdash@1.13.1
  │ │   │ └── assert-plus@1.0.0
  │ │   ├── ecc-jsbn@0.1.1
  │ │   ├─┬ getpass@0.1.6
  │ │   │ └── assert-plus@1.0.0
  │ │   ├── jodid25519@1.0.2
  │ │   ├── jsbn@0.1.0
  │ │   └── tweetnacl@0.13.3
  │ ├── is-typedarray@1.0.0
  │ ├── isstream@0.1.2
  │ ├── json-stringify-safe@5.0.1
  │ ├─┬ mime-types@2.1.11
  │ │ └── mime-db@1.23.0
  │ ├── node-uuid@1.4.7
  │ ├── oauth-sign@0.8.1
  │ ├── qs@6.1.0
  │ ├── stringstream@0.0.5
  │ ├── tough-cookie@2.2.2
  │ └── tunnel-agent@0.4.2
  ├─┬ rimraf@2.5.2
  │ └── glob@7.0.3
  ├─┬ sane@1.3.4
  │ ├─┬ exec-sh@0.2.0
  │ │ └── merge@1.2.0
  │ ├─┬ fb-watchman@1.9.0
  │ │ └─┬ bser@1.0.2
  │ │   └── node-int64@0.4.0
  │ ├─┬ minimatch@0.2.14
  │ │ ├── lru-cache@2.7.3
  │ │ └── sigmund@1.0.1
  │ ├── minimist@1.2.0
  │ ├─┬ walker@1.0.7
  │ │ └─┬ makeerror@1.0.11
  │ │   └── tmpl@1.0.4
  │ └── watch@0.10.0
  ├── semver@5.1.0
  ├─┬ systemjs@0.19.27
  │ └── when@3.7.7
  ├─┬ systemjs-builder@0.15.16
  │ ├─┬ babel-core@6.8.0
  │ │ ├─┬ babel-code-frame@6.8.0
  │ │ │ ├── esutils@2.0.2
  │ │ │ └── js-tokens@1.0.3
  │ │ ├─┬ babel-generator@6.8.0
  │ │ │ ├─┬ detect-indent@3.0.1
  │ │ │ │ ├── get-stdin@4.0.1
  │ │ │ │ └── minimist@1.2.0
  │ │ │ ├─┬ is-integer@1.0.6
  │ │ │ │ └─┬ is-finite@1.0.1
  │ │ │ │   └── number-is-nan@1.0.0
  │ │ │ ├── repeating@1.1.3
  │ │ │ └── trim-right@1.0.1
  │ │ ├── babel-helpers@6.8.0
  │ │ ├── babel-messages@6.8.0
  │ │ ├─┬ babel-register@6.8.0
  │ │ │ ├── core-js@2.3.0
  │ │ │ └─┬ home-or-tmp@1.0.0
  │ │ │   ├── os-tmpdir@1.0.1
  │ │ │   └── user-home@1.1.1
  │ │ ├─┬ babel-runtime@6.6.1
  │ │ │ └── core-js@2.3.0
  │ │ ├── babel-template@6.8.0
  │ │ ├─┬ babel-traverse@6.8.0
  │ │ │ ├── globals@8.18.0
  │ │ │ └─┬ invariant@2.2.1
  │ │ │   └── loose-envify@1.1.0
  │ │ ├─┬ babel-types@6.8.1
  │ │ │ └── to-fast-properties@1.0.2
  │ │ ├─┬ babylon@6.7.0
  │ │ │ └── babel-runtime@5.8.38
  │ │ ├── convert-source-map@1.2.0
  │ │ ├─┬ debug@2.2.0
  │ │ │ └── ms@0.7.1
  │ │ ├── json5@0.4.0
  │ │ ├── lodash@3.10.1
  │ │ ├── minimatch@2.0.10
  │ │ ├── path-exists@1.0.0
  │ │ ├── private@0.1.6
  │ │ ├── shebang-regex@1.0.0
  │ │ └── slash@1.0.0
  │ ├─┬ babel-plugin-transform-es2015-modules-systemjs@6.8.0
  │ │ ├── babel-helper-hoist-variables@6.8.0
  │ │ └── babel-plugin-transform-strict-mode@6.8.0
  │ ├─┬ es6-template-strings@2.0.0
  │ │ ├─┬ es5-ext@0.10.11
  │ │ │ ├── es6-iterator@2.0.0
  │ │ │ └── es6-symbol@3.0.2
  │ │ └─┬ esniff@1.0.0
  │ │   └── d@0.1.1
  │ ├── glob@7.0.3
  │ ├─┬ rollup@0.25.8
  │ │ ├── minimist@1.2.0
  │ │ └─┬ source-map-support@0.3.3
  │ │   └── source-map@0.1.32
  │ └── source-map@0.5.6
  ├─┬ traceur@0.0.105
  │ ├─┬ commander@2.9.0
  │ │ └── graceful-readlink@1.0.1
  │ ├── glob@5.0.15
  │ ├── semver@4.3.6
  │ └─┬ source-map-support@0.2.10
  │   └─┬ source-map@0.1.32
  │     └── amdefine@1.0.0
  └─┬ uglify-js@2.6.2
    ├── async@0.2.10
    ├── uglify-to-browserify@1.0.2
    └─┬ yargs@3.10.0
      ├── camelcase@1.2.1
      ├─┬ cliui@2.1.0
      │ ├─┬ center-align@0.1.3
      │ │ ├─┬ align-text@0.1.4
      │ │ │ ├─┬ kind-of@3.0.3
      │ │ │ │ └── is-buffer@1.1.3
      │ │ │ ├── longest@1.0.1
      │ │ │ └── repeat-string@1.5.4
      │ │ └── lazy-cache@1.0.4
      │ ├── right-align@0.1.3
      │ └── wordwrap@0.0.2
      ├── decamelize@1.2.0
      └── window-size@0.1.0
```


### Configuring jspm for the first time

Next, it's time to initialize the JSPM configuration, in a way that works well
with `django.contrib.staticfiles`.

For this project, the `STATIC_ROOT` is the directory `staticfiles`. It's where
the static files from the project/apps are copied to. This folder is normally
excluded from version control.

So, setting up jspm:

```sh
jspm init
```

This kicks of another interactive terminal session:

```
Init Mode (Quick, Standard, Custom) [Quick]: Custom
```

We pick `Custom`, for maximum control about which file is put where.

```
Prefix package.json properties under jspm? [Yes]: <enter>
```
Namespaces are good, let's do more of them!

```
     Enter a name for the project package.

     This name will be used for importing local code.
     eg via System.import('jspm_0_17/module.js').

Local package name (recommended, optional): jspm_0_17 <enter>
```
The name is derived from `package.json`.

```
     Enter the path to the folder containing the local project code.

     This is the folder containing the jspm_0_17 package code.

package.json directories.lib [src]: staticfiles/js
```
This is where it gets a bit tricky for a non-javascript-only project. Point this
to the folder that holds your javascript. For example, in this project, in all
`static` subfolders there is a `js` folder containing the javascript. Within
the `js` folder you can do the app-namespacing.

For JSPM, you should consider all `*/static/*` folders as one - just like the
result of `collectstatic`.

```
     Enter the file path to the public folder served to the browser.

     By default this is taken to be the root project folder.

package.json directories.baseURL (optional): staticfiles
```
In essence, this boils down to 'the parent of `directories.lib`' in the
previous question.

```
     Enter the path to the jspm packages folder.

     Only necessary if you would like to customize this folder name or
     location.

package.json directories.packages [staticfiles/jspm_packages]: <enter>
```
This is installing straight into `collectstatic`, because it has to be within
`baseURL`. The custom finder in systemjs ensures that files are served.

```
     Enter a custom config file path.

     Only necessary if you would like to customize the config file name or
     location.

package.json configFiles.jspm [staticfiles/jspm.config.js]: static/jspm.config.js
```
The same goes here - make sure that it can be found by `django.contrib.staticfiles`.
This config file should be kept in version control.

This configuration file holds the flattened dependency tree and translates package
imports to specific versions to load. Consider it the equivalent of a `requirements.txt`
where all the dependencies are pinned to a known functioning version.

The first section of this file can be hand-edited, the second section is auto-
generated and will be overwritten by jspm.

```

     Enter a custom browser config file path.

     This is also a SystemJS config file, but for browser-only jspm
     configurations.

package.json configFiles.jspm:browser [staticfiles/jspm.browser.js]: static/jspm.browser.js
```
Same remark as above.

This sets up some basepaths and basic browser-related configuration. It should
generally not be hand-edited.

```
     Enter the browser baseURL.

     This is the absolute URL of the directories.baseURL public folder in
     the browser.

System.config browser baseURL (optional): /static/
```
This url **must** match your `STATIC_URL` setting.

```

     Enter the browser URL for the folder containing the local project
     code.

     This should be the served directories.lib folder. Leave out the
     leading / to set a baseURL-relative path.

System.config browser URL to staticfiles/js  [js]: <enter>
```
This is useful for mapping the project namespace to the actual location that
will be served. In this case, modules in `jspm_0_17/foo/bar.js` will actually
make a request for `/static/js/foo/bar.js`.

```
     Enter the browser URL for the jspm_packages folder.

     Leave out the leading / to set a baseURL-relative path.

System.config browser URL to staticfiles/jspm_packages [jspm_packages]: <enter>
```
The default is correct here.

```
     Enter the main entry point of your package within the static/js
     folder.

System.config local package main [jspm_0_17.js]: main.js
```
We have the file `static/js/main.js`, so point to that actual file.

```
     Enter the module format of your local project code (within
     `static/js`).

     The default option is esm (ECMAScript Module).

System.config local package format (esm, cjs, amd): esm <enter>
```
The future is now, so stick with an official spec!

```
     Select a transpiler to use for ES module conversion.

     The transpiler is used when detecting modules with import or export
     statements, or for modules with format: "esm" metadata set.

System.config transpiler (Babel, Traceur, TypeScript, None) [babel]: <enter>
```
Good default, stick with it, unless you know why not. You can switch them around
anyway if you want.

After this, JSPM sets up the basic dependencies, such as downloading babel.

```
     Updating registry cache...
ok   Installed dev dependency plugin-babel to npm:systemjs-plugin-babel@^0.0.9
     (0.0.9)
     Install tree has no forks.

ok   Verified package.json at package.json
     Verified config files at static/jspm.config.js and static/jspm.browser.js
     Looking up loader files...
       system.js
       system.js.map
       system.src.js
       system-polyfills.js
       system-polyfills.src.js
       system-polyfills.js.map

     Using loader versions:
       systemjs@0.19.27
ok   Loader files downloaded successfully
```

## Loading your own code

Next, I've added a simple dummy app to load the template and staticfiles:

```
myapp
├── static
│   └── js
│       └── myapp
│           └── app.js
└── templates
    └── base.html

3 directories, 2 files
```

In `static/main.js` we perform an import to our project-namespaced and then
app-namespaced module.


## Bundling for production

Generate the production bundle(s) with
```sh
python manage.py systemjs_bundle --minify
```

```
Bundled jspm_0_17/main.js into SYSTEMJS/jspm_0_17/main.js
```

That file resides in `staticfiles/SYSTEMJS/jspm_0_17/main.js`, and the contents
are:

```javascript
System.registerDynamic("npm:systemjs-plugin-babel@0.0.9.json",[],!1,function(){return{main:"plugin-babel.js",map:{"systemjs-babel-build":{browser:"./systemjs-babel-browser.js","default":"./systemjs-babel-browser.js"}},meta:{"./plugin-babel.js":{format:"cjs"}}}}),System.register("npm:systemjs-plugin-babel@0.0.9/babel-helpers/classCallCheck.js",[],function(a,b){return{setters:[],execute:function(){a("default",function(a,b){if(!(a instanceof b))throw new TypeError("Cannot call a class as a function")})}}}),System.register("jspm_0_17/myapp/app.js",["npm:systemjs-plugin-babel@0.0.9/babel-helpers/classCallCheck.js"],function(a,b){var c,d;return{setters:[function(a){c=a["default"]}],execute:function(){d=function b(){c(this,b),document.getElementById("js-hook").innerText="myapp/app.js was loaded"},a("default",d)}}}),System.register("jspm_0_17/main.js",["jspm_0_17/myapp/app.js"],function(a,b){var c;return{setters:[function(a){c=a["default"]}],execute:function(){new c}}});
System.import('jspm_0_17/main.js');
//# sourceMappingURL=main.js.map
```


## Fast development workflow

It's also possible to have fast development work, which is particularly useful
when dealing with a lot of dependencies that take a long time to download.

Two components are relevant here:

* watching files for changes
* doing incremental builds and injecting the configuration with JSPM.

### Watch files for changes

You will need a global install of gulp (if you haven't yet):

```sh
npm install -g gulp
```

Next, make sure you have a local `gulp` and `gulp-watch`:
```sh
npm install gulp gulp-watch --save-dev
```

And create your `gulpfile.js` (it's in the repo).

Start `gulp`, and it will watch file changes in each `static` directory. If the
file is changed, it will be copied to `staticfiles` (similar to `collectstatic`).


### Bundle your application incrementally

The JSPM beta has a nice feature where you can watch the files involved for a
bundle, and watch them for changes. Only the changes are then recompilet,
resulting in a fast development process. The bundle is then injected in the
browser config, where it's loaded by SystemJS for the fastest development
experience.

In a different shell (or shell tab), run:

```
jspm bundle jspm_0_17/main.js staticfiles/SYSTEMJS/bundles/main.js -wid
```

`-w` makes sure the files are being watched,
`-i` injects the bundle (`SYSTEMJS/bundles/main.js`) into the browser config, and
`-d` bundles in `dev` mode where optimizations are skipped, minification is skipped etc.

Output:

```
     Building the bundle tree for jspm_0_17/main.js...

       jspm_0_17/main.js
       jspm_0_17/myapp/app.js
       npm:systemjs-plugin-babel@0.0.9.json
       npm:systemjs-plugin-babel@0.0.9/babel-helpers/classCallCheck.js

ok   SYSTEMJS/bundles/main.js added to config bundles.
ok   Built into staticfiles/SYSTEMJS/bundles/main.js with source maps,
     unminified.
     Watching staticfiles/js for changes with Watchman...

```

It has an (optional) dependency on Facebooks Watchman.

### Summary

With these things combined, you have 3 processes running, each in its own
shell / shell tab / screen or tmux session:

`python manage.py runserver`, `gulp` and `jspm bundle <...>`.
