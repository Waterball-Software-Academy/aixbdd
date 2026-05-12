process.env.TS_NODE_PROJECT = 'tsconfig.test.json'
process.env.TS_NODE_TRANSPILE_ONLY = 'true'

module.exports = {
  default: {
    requireModule: ['ts-node/register'],
    require: ['support/hooks.ts', '{{STEPS_DIR}}/**/*.steps.ts'],
    paths: ['{{FRONTEND_FEATURES_DIR}}/**/*.feature'],
    format: ['progress', 'summary'],
    timeout: 60000,
  },
}
