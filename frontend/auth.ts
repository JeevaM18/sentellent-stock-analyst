import NextAuth from "next-auth"
import GoogleProvider from "next-auth/providers/google"
import CredentialsProvider from "next-auth/providers/credentials"

export const { handlers, auth, signIn, signOut } = NextAuth({
  providers: [
    ...(process.env.GOOGLE_CLIENT_ID && process.env.GOOGLE_CLIENT_SECRET
      ? [
          GoogleProvider({
            clientId: process.env.GOOGLE_CLIENT_ID,
            clientSecret: process.env.GOOGLE_CLIENT_SECRET,
          }),
        ]
      : []),
    CredentialsProvider({
      id: "google-dev",
      name: "Google Account Login",
      credentials: {
        email: { label: "Email", type: "email" },
        name: { label: "Name", type: "text" },
        picture: { label: "Picture", type: "text" },
      },
      async authorize(credentials) {
        const email = (credentials?.email as string) || "jeeva59128@gmail.com";
        const name = (credentials?.name as string) || "Jeeva M";
        const picture = (credentials?.picture as string) || "https://lh3.googleusercontent.com/a/ACg8ocL-example";
        return {
          id: email,
          email: email,
          name: name,
          image: picture,
        };
      },
    }),
  ],
  secret:
    process.env.AUTH_SECRET ||
    process.env.NEXTAUTH_SECRET ||
    "ba33e4914440fff6ceb17f4d868656e11b2cce74de5dd1368bbc8b04ade5bcfb",
  callbacks: {
    async signIn() {
      return true
    },
    async session({ session, token }) {
      if (session.user && token.sub) {
        session.user.id = token.sub
      }
      session.auth = {
        googleIdToken: (token.googleIdToken as string) || "dev-sentellent-auth-token",
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
