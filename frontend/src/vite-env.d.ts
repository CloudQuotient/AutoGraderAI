/// <reference types="vite/client" />

declare interface ImportMetaEnv {
  readonly VITE_API_BASE_URL: string;
  readonly VITE_AWS_REGION: string;
  readonly VITE_COGNITO_POOL_ID: string;
  readonly VITE_COGNITO_CLIENT_ID: string;
  readonly VITE_DEMO_MODE: string;
}

declare interface ImportMeta {
  readonly env: ImportMetaEnv;
}
