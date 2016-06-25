class BundleOptionsMixin(object):

    def add_arguments(self, parser):
        super(BundleOptionsMixin, self).add_arguments(parser)

        parser.add_argument(
            '--sfx',
            action='store_true', dest='sfx',
            help="Generate self-executing bundles.")

        parser.add_argument(
            '--node-path', default='./node_modules',
            help='Path to the project `node_modules` directory')
        parser.add_argument('--minify', action='store_true', help='Let jspm minify the bundle')
        parser.add_argument('--minimal', action='store_true', help='Only (re)bundle if changes detected')

    def get_system_opts(self, options):
        system_options = ['minimal', 'minify', 'sfx']
        return {opt: options.get(opt) for opt in system_options}
