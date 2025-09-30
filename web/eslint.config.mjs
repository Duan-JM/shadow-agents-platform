import { FlatCompat } from '@eslint/eslintrc'

const compat = new FlatCompat({
  baseDirectory: import.meta.dirname,
})

const eslintConfig = [
  ...compat.extends('next/core-web-vitals', 'next/typescript'),
  {
    rules: {
      // 关闭一些严格规则
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': ['warn', { argsIgnorePattern: '^_' }],
      'react-hooks/exhaustive-deps': 'warn',
      // 强制使用单引号
      'quotes': ['error', 'single', { avoidEscape: true }],
      // 强制使用分号
      'semi': ['error', 'never'],
      // 禁止 console（生产环境）
      'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    },
  },
]

export default eslintConfig
