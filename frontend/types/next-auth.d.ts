import { DefaultSession } from "next-auth"

declare module "next-auth" {
  interface Session {
    user: {
      id?: string
    } & DefaultSession["user"]
    auth?: {
      googleIdToken?: string
    }
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    idToken?: string
    googleIdToken?: string
  }
}
