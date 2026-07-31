import NextAuth from "next-auth"
import GoogleProvider from "next-auth/providers/google"

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID || "",
      clientSecret: process.env.GOOGLE_CLIENT_SECRET || "",
    }),
  ],
  secret:
    process.env.AUTH_SECRET ||
    process.env.NEXTAUTH_SECRET ||
    "ba33e4914440fff6ceb17f4d868656e11b2cce74de5dd1368bbc8b04ade5bcfb",
  callbacks: {
    async signIn({ user, account, profile }) {
      return true
    },
    async session({ session, token }) {
      if (session.user && token.sub) {
        session.user.id = token.sub
      }
      // Expose session.auth.googleIdToken for FastAPI Bearer token Authorization headers
      session.auth = {
        googleIdToken: (token.googleIdToken as string) || "",
      }
      return session
    },
    async jwt({ token, user, account }) {
      if (user) {
        token.id = user.id
      }
      if (account?.id_token) {
        token.googleIdToken = account.id_token
      }
      return token
    },
  },
})
