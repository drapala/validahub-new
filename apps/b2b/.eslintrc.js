module.exports = {
  extends: ["next/core-web-vitals"],
  rules: {
    // ============================================
    // ARCHITECTURAL RULES
    // ============================================
    
    // Prevent UI components from importing adapters directly
    "no-restricted-imports": [
      "error",
      {
        patterns: [
          {
            group: ["*/adapters/*", "**/adapters/**"],
            message: "UI components should not import adapters directly. Use ports and use cases instead.",
          },
        ],
        paths: [
          {
            name: "next-auth/react",
            importNames: ["signIn", "signOut"],
            message: "Use auth use cases instead of calling NextAuth directly from UI components.",
          },
        ],
      },
    ],
    
    // Enforce import order
    "import/order": [
      "error",
      {
        groups: [
          "builtin",
          "external",
          "internal",
          ["parent", "sibling"],
          "index",
          "object",
          "type",
        ],
        pathGroups: [
          {
            pattern: "react",
            group: "external",
            position: "before",
          },
          {
            pattern: "@/core/**",
            group: "internal",
            position: "before",
          },
          {
            pattern: "@/components/**",
            group: "internal",
          },
          {
            pattern: "@/lib/**",
            group: "internal",
            position: "after",
          },
        ],
        pathGroupsExcludedImportTypes: ["react"],
        "newlines-between": "always",
        alphabetize: {
          order: "asc",
          caseInsensitive: true,
        },
      },
    ],
    
    // ============================================
    // CODE QUALITY RULES
    // ============================================
    
    // Enforce consistent naming
    "@typescript-eslint/naming-convention": [
      "warn",
      {
        selector: "interface",
        format: ["PascalCase"],
        prefix: ["I"],
        filter: {
          regex: "^(Props|State)$",
          match: false,
        },
      },
      {
        selector: "typeAlias",
        format: ["PascalCase"],
      },
      {
        selector: "enum",
        format: ["PascalCase"],
      },
      {
        selector: "enumMember",
        format: ["UPPER_CASE"],
      },
    ],
    
    // Prevent unused variables
    "@typescript-eslint/no-unused-vars": [
      "warn",
      {
        argsIgnorePattern: "^_",
        varsIgnorePattern: "^_",
      },
    ],
    
    // ============================================
    // REACT/NEXT.JS RULES
    // ============================================
    
    // Enforce React hooks rules
    "react-hooks/rules-of-hooks": "error",
    "react-hooks/exhaustive-deps": "warn",
    
    // Prevent missing key prop
    "react/jsx-key": "error",
    
    // Enforce self-closing tags
    "react/self-closing-comp": [
      "error",
      {
        component: true,
        html: true,
      },
    ],
    
    // ============================================
    // ACCESSIBILITY RULES
    // ============================================
    
    "jsx-a11y/alt-text": "error",
    "jsx-a11y/aria-props": "error",
    "jsx-a11y/aria-role": "error",
    "jsx-a11y/role-has-required-aria-props": "error",
    "jsx-a11y/heading-has-content": "error",
    "jsx-a11y/anchor-has-content": "error",
  },
  
  overrides: [
    {
      // Allow adapters to import from anywhere
      files: ["**/adapters/**/*.ts", "**/adapters/**/*.tsx"],
      rules: {
        "no-restricted-imports": "off",
      },
    },
    {
      // Use cases can import from ports and entities
      files: ["**/usecases/**/*.ts", "**/usecases/**/*.tsx"],
      rules: {
        "no-restricted-imports": [
          "error",
          {
            patterns: [
              {
                group: ["*/adapters/*", "**/adapters/**"],
                message: "Use cases should not import adapters directly. Use dependency injection.",
              },
              {
                group: ["*/components/*", "**/components/**"],
                message: "Use cases should not import UI components.",
              },
            ],
          },
        ],
      },
    },
    {
      // Ports should not import anything except entities
      files: ["**/ports/**/*.ts"],
      rules: {
        "no-restricted-imports": [
          "error",
          {
            patterns: [
              {
                group: ["*/adapters/*", "**/adapters/**", "*/usecases/*", "**/usecases/**", "*/components/*", "**/components/**"],
                message: "Ports should only define interfaces and not import implementations.",
              },
            ],
          },
        ],
      },
    },
  ],
}